import re
import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.level import Level, UserLevelProgress
from app.models.achievement import Achievement, UserAchievement
from app.models.test_case import TestCase as TestCaseModel
from app.routers.auth import get_current_user
from app.sandbox import run_code_sandbox

router = APIRouter(prefix="/api/levels", tags=["levels"])


async def _check_achievements(user_id: int, db: AsyncSession) -> list[dict]:
    """Detect and award new achievements for a user. Returns list of newly earned."""
    new_achievements = []
    all_ach = (await db.execute(select(Achievement))).scalars().all()
    earned = (await db.execute(
        select(UserAchievement.achievement_key).where(UserAchievement.user_id == user_id)
    )).scalars().all()
    earned_set = set(earned)

    # Short-circuit: if all achievements already earned, skip expensive queries
    if len(earned_set) >= len(all_ach):
        return []

    # Pre-compute counts to avoid N+1 queries
    total_completed = None
    stage_counts = {}
    lab_visit_count = None

    for ach in all_ach:
        if ach.key in earned_set:
            continue
        if ach.condition_type == "completed_count" and total_completed is None:
            total_completed = (await db.execute(
                select(func.count(UserLevelProgress.id))
                .where(UserLevelProgress.user_id == user_id, UserLevelProgress.status == "completed")
            )).scalar() or 0
        elif ach.condition_type == "stage_done" and ach.condition_value not in stage_counts:
            stage = ach.condition_value
            stage_levels = (await db.execute(select(Level.id).where(Level.stage == stage))).scalars().all()
            stage_ids = list(stage_levels)
            if stage_ids:
                done = (await db.execute(
                    select(func.count(UserLevelProgress.id))
                    .where(UserLevelProgress.user_id == user_id,
                           UserLevelProgress.level_id.in_(stage_ids),
                           UserLevelProgress.status == "completed")
                )).scalar() or 0
                stage_counts[stage] = (done, len(stage_ids))
            else:
                stage_counts[stage] = (0, 1)
        elif ach.condition_type == "lab_count" and lab_visit_count is None:
            lab_user = (await db.execute(select(User).where(User.id == user_id))).scalar_one()
            lab_visit_count = lab_user.lab_visit_count or 0

    for ach in all_ach:
        if ach.key in earned_set:
            continue
        earn = False
        if ach.condition_type == "completed_count":
            earn = total_completed >= int(ach.condition_value)
        elif ach.condition_type == "stage_done":
            done, total = stage_counts.get(ach.condition_value, (0, 1))
            earn = done >= total
        elif ach.condition_type == "lab_count":
            earn = lab_visit_count >= int(ach.condition_value)

        if earn:
            db.add(UserAchievement(user_id=user_id, achievement_key=ach.key))
            new_achievements.append({"key": ach.key, "name": ach.name, "desc": ach.desc})

    return new_achievements


class SubmitAnswer(BaseModel):
    level_id: int
    answer: dict


@router.get("")
async def list_levels(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Level).order_by(Level.order))
    all_levels = result.scalars().all()
    level_ids = [l.id for l in all_levels]
    progress_result = await db.execute(
        select(UserLevelProgress).where(UserLevelProgress.user_id == user.id, UserLevelProgress.level_id.in_(level_ids)))
    progress_map = {p.level_id: p for p in progress_result.scalars().all()}

    if all_levels and not any(l.id in progress_map for l in all_levels):
        first = all_levels[0]
        prog = UserLevelProgress(user_id=user.id, level_id=first.id, status="unlocked")
        db.add(prog); await db.commit()
        progress_map[first.id] = prog

    # Batch unlock: determine locked levels whose prerequisite is completed
    level_by_order = {l.order: l for l in all_levels}
    sorted_orders = sorted(level_by_order.keys())
    order_index = {order: i for i, order in enumerate(sorted_orders)}
    unlocked_ids = set()
    for l in all_levels:
        p = progress_map.get(l.id)
        if not p or p.status == "locked":
            prereq_id = l.required_level_id
            if prereq_id:
                prereq_p = progress_map.get(prereq_id)
                if prereq_p and prereq_p.status == "completed":
                    unlocked_ids.add(l.id)
            else:
                idx = order_index.get(l.order, -1)
                if idx > 0:
                    prev_order = sorted_orders[idx - 1]
                    prev = level_by_order.get(prev_order)
                    if prev:
                        prev_p = progress_map.get(prev.id)
                        if prev_p and prev_p.status == "completed":
                            unlocked_ids.add(l.id)

    if unlocked_ids:
        for l in all_levels:
            if l.id in unlocked_ids:
                p = UserLevelProgress(user_id=user.id, level_id=l.id, status="unlocked")
                db.add(p)
                progress_map[l.id] = p
        await db.commit()

    levels_out = []
    for l in all_levels:
        p = progress_map.get(l.id)
        status = p.status if p else "locked"
        levels_out.append({
            "id": l.id, "order": l.order, "stage": l.stage, "title": l.title,
            "description": l.description, "task_type": l.task_type, "points": l.points,
            "tool_id": l.tool_id, "status": status,
            "score": p.score if p else 0, "attempts": p.attempts if p else 0,
        })

    stages = {}
    for l in levels_out:
        s = l["stage"]
        stages.setdefault(s, {"total": 0, "completed": 0, "points": 0, "max_points": 0})
        stages[s]["total"] += 1; stages[s]["max_points"] += l["points"]
        if l["status"] == "completed":
            stages[s]["completed"] += 1; stages[s]["points"] += l["points"]

    total_completed = sum(s["completed"] for s in stages.values())
    total_levels = sum(s["total"] for s in stages.values())
    total_points = sum(s["points"] for s in stages.values())
    return {"levels": levels_out, "stages": stages, "progress": {"completed": total_completed, "total": total_levels, "points": total_points}}


@router.get("/{level_id}")
async def get_level(level_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Level).where(Level.id == level_id))
    level = result.scalar_one_or_none()
    if not level:
        raise HTTPException(status_code=404)
    pr = await db.execute(select(UserLevelProgress).where(
        UserLevelProgress.user_id == user.id, UserLevelProgress.level_id == level_id))
    progress = pr.scalar_one_or_none()
    if not progress or progress.status == "locked":
        raise HTTPException(status_code=403)
    if progress.status == "unlocked":
        progress.status = "in_progress"; progress.started_at = datetime.now(timezone.utc); await db.commit()
    return {
        "id": level.id, "order": level.order, "stage": level.stage, "title": level.title,
        "description": level.description, "theory": level.theory, "demo": level.demo,
        "task_type": level.task_type, "task_config": level.task_config, "points": level.points,
        "status": progress.status, "attempts": progress.attempts,
    }


@router.post("/{level_id}/run")
async def run_level_code(level_id: int, data: SubmitAnswer,
                         user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    lr = await db.execute(select(Level).where(Level.id == level_id))
    level = lr.scalar_one_or_none()
    if not level or level.task_type not in ("code", "debug"):
        raise HTTPException(status_code=400, detail="Not a code or debug level")
    pr = await db.execute(select(UserLevelProgress).where(
        UserLevelProgress.user_id == user.id, UserLevelProgress.level_id == level_id))
    progress = pr.scalar_one_or_none()
    if not progress or progress.status == "locked":
        raise HTTPException(status_code=403, detail="Level not unlocked")
    code = data.answer.get("code", "")
    test_input = level.task_config.get("test_input", "")
    # to_thread: subprocess run blocks up to SANDBOX_TIMEOUT (QA-2026-08-18 HIGH #6)
    return await asyncio.to_thread(run_code_sandbox, code, test_input)


@router.post("/submit")
async def submit_answer(data: SubmitAnswer, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    lr = await db.execute(select(Level).where(Level.id == data.level_id))
    level = lr.scalar_one_or_none()
    if not level:
        raise HTTPException(status_code=404)
    pr = await db.execute(select(UserLevelProgress).where(
        UserLevelProgress.user_id == user.id, UserLevelProgress.level_id == data.level_id))
    progress = pr.scalar_one_or_none()
    if not progress:
        raise HTTPException(status_code=403)

    progress.attempts += 1; progress.answer = data.answer
    score = 0; correct = False; explanation = ""

    if level.task_type == "quiz":
        user_choice = data.answer.get("choice")
        correct_idx = level.task_config.get("correct_index")
        if correct_idx is None:
            raise HTTPException(status_code=500, detail="Quiz config missing correct_index")
        correct = (user_choice == correct_idx)
        score = 100 if correct else 0
        explanation = level.task_config.get("explanation", "")

    elif level.task_type == "code":
        code = data.answer.get("code", "")
        test_input = level.task_config.get("test_input", "")
        expected = level.task_config.get("expected", "")
        sandbox_result = await asyncio.to_thread(run_code_sandbox, code, test_input)
        if sandbox_result["ok"]:
            actual = sandbox_result["stdout"]
            if expected and actual == expected:
                correct = True; score = 100; explanation = f"输出匹配: {actual}"
            elif expected:
                score = int(min(len(actual) / max(len(expected), 1) * 100, 90))
                explanation = f"期望: {expected}\n实际: {actual}"
            elif sandbox_result["returncode"] == 0:
                correct = True; score = 90; explanation = f"代码执行成功: {actual}"
            else:
                score = 10; explanation = f"错误: {sandbox_result.get('stderr', '')}"
        else:
            score = 0; explanation = sandbox_result.get("error", "Unknown error")

    elif level.task_type == "debug":
        code = data.answer.get("code", "")
        test_input = level.task_config.get("test_input", "")
        sandbox_result = await asyncio.to_thread(run_code_sandbox, code, test_input)
        if sandbox_result["ok"] and sandbox_result["returncode"] == 0:
            checks = level.task_config.get("checks", [])
            passed_checks = 0
            for chk in checks:
                if re.search(chk, code):
                    passed_checks += 1
            if passed_checks == len(checks):
                correct = True; score = 100; explanation = f"Debug成功！已修复所有 {len(checks)} 个检查点。"
            else:
                score = int(passed_checks / max(len(checks), 1) * 70)
                explanation = f"代码能运行，但通过了 {passed_checks}/{len(checks)} 个检查。还需继续修复。"
        else:
            score = 10; explanation = sandbox_result.get("error", sandbox_result.get("stderr", "代码仍有错误，请继续修复"))

    elif level.task_type == "scenario":
        user_choice = data.answer.get("choice")
        correct_idx = level.task_config.get("correct_index")
        if correct_idx is None:
            raise HTTPException(status_code=500, detail="Scenario config missing correct_index")
        correct = (user_choice == correct_idx)
        score = 100 if correct else 0
        explanation = level.task_config.get("explanation", "")
        # Include per-option analysis for learning depth
        if not correct:
            option_analysis = level.task_config.get("option_analysis", [])
            if option_analysis and isinstance(user_choice, int) and 0 <= user_choice < len(option_analysis):
                explanation += "\n\n" + option_analysis[user_choice]

    elif level.task_type == "explore":
        user_answer = data.answer.get("text", "")
        keywords = level.task_config.get("keywords", [])
        matched = sum(1 for kw in keywords if kw in user_answer)
        score = int(matched / max(len(keywords), 1) * 100)
        correct = score >= 60

    elif level.task_type == "analyze":
        user_choice = data.answer.get("choice")
        correct_idx = level.task_config.get("correct_index")
        if correct_idx is None:
            raise HTTPException(status_code=500, detail="Analyze config missing correct_index")
        correct = (user_choice == correct_idx)
        score = 100 if correct else 0
        explanation = level.task_config.get("explanation", "")

    if correct or score >= 70:
        progress.status = "completed"; progress.score = max(progress.score, score)
        progress.completed_at = datetime.now(timezone.utc)

    await db.commit()

    new_achievements = []
    if progress.status == "completed":
        new_achievements = await _check_achievements(user.id, db)
        if new_achievements:
            try:
                await db.commit()
            except Exception:
                await db.rollback()  # concurrent request may have already awarded

    return {"correct": correct, "score": score, "explanation": explanation,
            "attempts": progress.attempts, "completed": progress.status == "completed",
            "new_achievements": new_achievements}


@router.get("/{level_id}/testcases")
async def get_level_testcases(level_id: int,
                               user: User = Depends(get_current_user),
                               db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TestCaseModel).where(
            TestCaseModel.level_id == level_id,
            TestCaseModel.user_id == user.id
        ).order_by(TestCaseModel.updated_at.desc())
    )
    cases = result.scalars().all()
    return {"testcases": [{
        "id": c.id, "title": c.title, "priority": c.priority,
        "status": c.status, "folder": c.folder,
    } for c in cases]}
