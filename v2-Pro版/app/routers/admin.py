"""Admin endpoints for QA通关."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func, delete as sa_delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.models.level import Level, UserLevelProgress
from app.routers.auth import get_current_user
from app.config import ADMIN_PAGE_LIMIT

router = APIRouter(prefix="/api/admin", tags=["admin"])


async def _require_admin(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/stats")
async def get_stats(admin: User = Depends(_require_admin), db: AsyncSession = Depends(get_db)):
    # User stats
    user_count = (await db.execute(select(func.count(User.id)))).scalar()
    active_users = (await db.execute(
        select(func.count(func.distinct(UserLevelProgress.user_id)))
    )).scalar()

    # Level stats
    total_levels = (await db.execute(select(func.count(Level.id)))).scalar()
    completed_total = (await db.execute(
        select(func.count(UserLevelProgress.id)).where(UserLevelProgress.status == "completed")
    )).scalar()

    # Completion distribution
    completions = (await db.execute(
        select(UserLevelProgress.user_id, func.count(UserLevelProgress.id))
        .where(UserLevelProgress.status == "completed")
        .group_by(UserLevelProgress.user_id)
    )).all()

    return {
        "users": {"total": user_count, "active": active_users},
        "levels": {"total": total_levels, "completions": completed_total},
        "completion_distribution": [{"user_id": uid, "completed": cnt} for uid, cnt in completions],
    }


@router.get("/users")
async def list_users(admin: User = Depends(_require_admin), db: AsyncSession = Depends(get_db),
                     limit: int = Query(ADMIN_PAGE_LIMIT, ge=1, le=200), offset: int = Query(0, ge=0)):
    total = (await db.execute(select(func.count(User.id)))).scalar()
    result = await db.execute(select(User).order_by(User.id).offset(offset).limit(limit))
    users = result.scalars().all()

    # Get completion counts per user
    user_ids = [u.id for u in users]
    completion_counts = {}
    if user_ids:
        rows = (await db.execute(
            select(UserLevelProgress.user_id, func.count(UserLevelProgress.id))
            .where(UserLevelProgress.user_id.in_(user_ids), UserLevelProgress.status == "completed")
            .group_by(UserLevelProgress.user_id)
        )).all()
        completion_counts = {uid: cnt for uid, cnt in rows}

    return {
        "users": [
            {
                "id": u.id, "username": u.username, "email": u.email,
                "is_admin": u.is_admin, "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "levels_completed": completion_counts.get(u.id, 0),
            }
            for u in users
        ],
        "total": total,
    }


# ==================== Level Management ====================

class LevelUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    theory: str | None = None
    demo: str | None = None
    stage: str | None = None
    task_type: str | None = None
    task_config: dict | None = None
    points: int | None = None
    order: int | None = None


class LevelCreate(BaseModel):
    title: str
    stage: str = "beginner"
    task_type: str = "quiz"
    points: int = 10
    order: int | None = None
    description: str = ""
    theory: str = ""
    demo: str | None = None
    task_config: dict = {}


class ReorderRequest(BaseModel):
    items: list[dict]  # [{id: 1, order: 1}, {id: 2, order: 2}, ...]


@router.get("/levels")
async def list_levels(admin: User = Depends(_require_admin),
                      db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Level).order_by(Level.order))
    levels = r.scalars().all()
    return {"levels": [
        {
            "id": lv.id, "order": lv.order, "stage": lv.stage,
            "title": lv.title, "description": lv.description,
            "theory": lv.theory, "demo": lv.demo,
            "task_type": lv.task_type, "task_config": lv.task_config,
            "points": lv.points,
        }
        for lv in levels
    ]}



@router.put("/levels/reorder")
async def reorder_levels(data: ReorderRequest,
                         admin: User = Depends(_require_admin),
                         db: AsyncSession = Depends(get_db)):
    ids = [item["id"] for item in data.items]
    r = await db.execute(select(Level).where(Level.id.in_(ids)))
    levels = {lv.id: lv for lv in r.scalars().all()}
    # Use temp negative orders to avoid unique constraint conflicts during swap
    for item in data.items:
        lv = levels.get(item["id"])
        if lv:
            lv.order = -item["order"]
    await db.flush()
    for item in data.items:
        lv = levels.get(item["id"])
        if lv:
            lv.order = item["order"]
    await db.commit()
    return {"ok": True}


@router.put("/levels/{level_id}")
async def update_level(level_id: int, data: LevelUpdate,
                       admin: User = Depends(_require_admin),
                       db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Level).where(Level.id == level_id))
    level = r.scalar_one_or_none()
    if not level:
        raise HTTPException(status_code=404)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(level, k, v)
    await db.commit()
    return {"ok": True, "id": level.id}


@router.post("/levels")
async def create_level(data: LevelCreate,
                       admin: User = Depends(_require_admin),
                       db: AsyncSession = Depends(get_db)):
    order = data.order
    if order is None:
        max_order = (await db.execute(select(func.max(Level.order)))).scalar() or 0
        order = max_order + 1
    for attempt in range(3):
        try:
            level = Level(order=order, stage=data.stage, title=data.title,
                          description=data.description, theory=data.theory,
                          demo=data.demo, task_type=data.task_type,
                          task_config=data.task_config, points=data.points)
            db.add(level)
            await db.commit()
            await db.refresh(level)
            return {"ok": True, "id": level.id, "order": level.order}
        except IntegrityError:
            await db.rollback()
            max_order = (await db.execute(select(func.max(Level.order)))).scalar() or 0
            order = max_order + 1
    raise HTTPException(status_code=409, detail="Could not create level due to order conflict")


@router.delete("/levels/{level_id}")
async def delete_level(level_id: int,
                       admin: User = Depends(_require_admin),
                       db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Level).where(Level.id == level_id))
    level = r.scalar_one_or_none()
    if not level:
        raise HTTPException(status_code=404)
    await db.execute(sa_delete(UserLevelProgress).where(UserLevelProgress.level_id == level_id))
    await db.delete(level)
    await db.commit()
    return {"ok": True}
