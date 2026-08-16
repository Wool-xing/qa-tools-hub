"""Learning analytics endpoints for QA通关."""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.models.level import Level, UserLevelProgress
from app.models.achievement import Achievement, UserAchievement
from app.routers.auth import get_current_user
from app.config import SKILL_GAP_WEAK_THRESHOLD, SKILL_GAP_STRONG_THRESHOLD, LEADERBOARD_LIMIT

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/progress-timeline")
async def progress_timeline(
    days: int = 90,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return daily completed count and points earned for the last N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(UserLevelProgress)
        .where(UserLevelProgress.user_id == user.id, UserLevelProgress.status == "completed",
               UserLevelProgress.completed_at >= cutoff)
        .order_by(UserLevelProgress.completed_at)
    )
    completed = result.scalars().all()

    # Build daily aggregation
    daily = {}
    for p in completed:
        if p.completed_at:
            day = p.completed_at.strftime("%Y-%m-%d")
            if day not in daily:
                daily[day] = {"completed": 0, "points": 0}
            daily[day]["completed"] += 1

    # Also get points from levels
    level_ids = [p.level_id for p in completed]
    if level_ids:
        lvl_result = await db.execute(select(Level).where(Level.id.in_(level_ids)))
        levels_map = {l.id: l.points for l in lvl_result.scalars().all()}
        for p in completed:
            if p.completed_at:
                day = p.completed_at.strftime("%Y-%m-%d")
                daily[day]["points"] += levels_map.get(p.level_id, 10)

    timeline = [{"date": d, "completed": v["completed"], "points": v["points"]}
                for d, v in sorted(daily.items())]

    return {"days": days, "timeline": timeline, "total_completed": len(completed)}


@router.get("/skill-gaps")
async def skill_gaps(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return per-stage average score and identify weakest areas."""
    # Get all completed progress for user
    result = await db.execute(
        select(UserLevelProgress)
        .where(UserLevelProgress.user_id == user.id, UserLevelProgress.status == "completed")
    )
    completed = result.scalars().all()

    if not completed:
        return {"stages": [], "weakest": [], "strongest": []}

    level_ids = [p.level_id for p in completed]
    lvl_result = await db.execute(select(Level).where(Level.id.in_(level_ids)))
    levels_map = {l.id: l for l in lvl_result.scalars().all()}

    # Aggregate by stage
    stages = {}
    for p in completed:
        lvl = levels_map.get(p.level_id)
        if not lvl:
            continue
        stage = lvl.stage
        if stage not in stages:
            stages[stage] = {"total_score": 0, "total_attempts": 0, "count": 0, "level_ids": []}
        stages[stage]["total_score"] += p.score
        stages[stage]["total_attempts"] += p.attempts
        stages[stage]["count"] += 1
        stages[stage]["level_ids"].append(lvl.id)

    # Compute stats
    stage_stats = []
    for stage, data in stages.items():
        avg_score = round(data["total_score"] / data["count"], 1) if data["count"] else 0
        avg_attempts = round(data["total_attempts"] / data["count"], 1) if data["count"] else 0
        stage_stats.append({
            "stage": stage,
            "completed": data["count"],
            "avg_score": avg_score,
            "avg_attempts": avg_attempts,
        })

    # Sort by avg_score ascending (weakest first)
    stage_stats.sort(key=lambda s: s["avg_score"])

    weakest = [s["stage"] for s in stage_stats[:3] if s["avg_score"] < SKILL_GAP_WEAK_THRESHOLD]
    strongest = [s["stage"] for s in stage_stats[-3:] if s["avg_score"] >= SKILL_GAP_STRONG_THRESHOLD]

    return {
        "stages": stage_stats,
        "weakest": weakest,
        "strongest": strongest,
        "recommendation": f"建议优先复习：{'、'.join(weakest) if weakest else '暂无薄弱领域，继续保持！'}",
    }


@router.get("/achievements")
async def get_achievements(user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)):
    # Get all achievement definitions
    all_ach = (await db.execute(select(Achievement))).scalars().all()

    # Get earned achievements
    earned = (await db.execute(
        select(UserAchievement).where(UserAchievement.user_id == user.id)
    )).scalars().all()
    earned_keys = {e.achievement_key for e in earned}

    return {
        "achievements": [{
            "key": a.key, "icon": a.icon, "name": a.name, "desc": a.desc,
            "earned": a.key in earned_keys,
            "earned_at": next((e.earned_at.isoformat() for e in earned if e.achievement_key == a.key), None),
        } for a in all_ach]
    }


@router.get("/leaderboard")
async def leaderboard(period: str = "weekly", db: AsyncSession = Depends(get_db)):
    """Top users by points/completed levels. period: weekly, monthly, alltime."""
    q = (select(User.username, func.count(UserLevelProgress.id).label("completed"), func.sum(Level.points).label("points"))
         .join(UserLevelProgress, UserLevelProgress.user_id == User.id)
         .join(Level, UserLevelProgress.level_id == Level.id)
         .where(UserLevelProgress.status == "completed"))

    if period == "weekly":
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        q = q.where(UserLevelProgress.completed_at >= cutoff)
    elif period == "monthly":
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        q = q.where(UserLevelProgress.completed_at >= cutoff)

    result = await db.execute(
        q.group_by(User.id, User.username)
        .order_by(func.count(UserLevelProgress.id).desc())
        .limit(LEADERBOARD_LIMIT)
    )
    rows = result.all()
    return {
        "leaderboard": [
            {"rank": i + 1, "username": row[0], "completed": row[1], "points": row[2] or 0}
            for i, row in enumerate(rows)
        ]
    }


@router.get("/export")
async def export_progress(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export user's complete learning progress as JSON."""
    result = await db.execute(
        select(UserLevelProgress).where(UserLevelProgress.user_id == user.id)
    )
    all_progress = result.scalars().all()

    level_ids = [p.level_id for p in all_progress]
    levels_map = {}
    if level_ids:
        lvl_result = await db.execute(select(Level).where(Level.id.in_(level_ids)))
        levels_map = {l.id: l for l in lvl_result.scalars().all()}

    progress_list = []
    for p in all_progress:
        lv = levels_map.get(p.level_id)
        progress_list.append({
            "level_id": p.level_id,
            "title": lv.title if lv else "Unknown",
            "stage": lv.stage if lv else "unknown",
            "task_type": lv.task_type if lv else "unknown",
            "status": p.status,
            "score": p.score,
            "attempts": p.attempts,
            "points": lv.points if lv else 0,
            "started_at": p.started_at.isoformat() if p.started_at else None,
            "completed_at": p.completed_at.isoformat() if p.completed_at else None,
        })

    total_points = sum(item["points"] for item in progress_list if item["status"] == "completed")
    completed_count = sum(1 for item in progress_list if item["status"] == "completed")

    return {
        "username": user.username,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_levels": len(progress_list),
            "completed": completed_count,
            "total_points": total_points,
        },
        "progress": progress_list,
    }
