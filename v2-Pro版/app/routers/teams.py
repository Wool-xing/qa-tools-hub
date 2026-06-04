"""Team collaboration endpoints for QA通关."""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.team import Team, TeamMember
from app.models.test_case import TestCase
from app.models.level import UserLevelProgress
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/teams", tags=["teams"])


class TeamCreate(BaseModel):
    name: str


class TeamJoin(BaseModel):
    invite_code: str


@router.post("")
async def create_team(data: TeamCreate, user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    if not (2 <= len(data.name) <= 50):
        raise HTTPException(status_code=400, detail="Team name must be 2-50 characters")
    invite_code = uuid.uuid4().hex[:8].upper()
    team = Team(name=data.name, invite_code=invite_code, created_by=user.id)
    db.add(team)
    await db.flush()
    member = TeamMember(team_id=team.id, user_id=user.id, role="owner")
    db.add(member)
    await db.commit()
    return {"id": team.id, "name": team.name, "invite_code": team.invite_code}


@router.post("/join")
async def join_team(data: TeamJoin, user: User = Depends(get_current_user),
                    db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Team).where(Team.invite_code == data.invite_code.strip().upper()))
    team = r.scalar_one_or_none()
    if not team:
        raise HTTPException(status_code=404, detail="Invalid invite code")

    # Check if already member
    existing = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team.id, TeamMember.user_id == user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already a member of this team")

    member = TeamMember(team_id=team.id, user_id=user.id, role="member")
    db.add(member)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Already a member of this team")
    return {"id": team.id, "name": team.name, "message": "Joined team successfully"}


@router.get("/mine")
async def list_my_teams(user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    r = await db.execute(
        select(TeamMember).where(TeamMember.user_id == user.id))
    memberships = r.scalars().all()
    if not memberships:
        return {"teams": []}

    team_ids = [m.team_id for m in memberships]
    team_result = await db.execute(select(Team).where(Team.id.in_(team_ids)))
    teams = team_result.scalars().all()

    # Get member counts in single query
    count_rows = (await db.execute(
        select(TeamMember.team_id, func.count(TeamMember.id))
        .where(TeamMember.team_id.in_(team_ids))
        .group_by(TeamMember.team_id)
    )).all()
    member_counts = {tid: cnt for tid, cnt in count_rows}

    return {
        "teams": [{
            "id": t.id, "name": t.name, "invite_code": t.invite_code,
            "role": next((m.role for m in memberships if m.team_id == t.id), "member"),
            "member_count": member_counts.get(t.id, 0),
            "created_at": t.created_at.isoformat() if t.created_at else None,
        } for t in teams]
    }


@router.get("/{team_id}/members")
async def list_members(team_id: int, user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    # Verify membership
    r = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user.id))
    if not r.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not a team member")

    # Get all members with usernames
    result = await db.execute(
        select(TeamMember, User.username)
        .join(User, TeamMember.user_id == User.id)
        .where(TeamMember.team_id == team_id)
    )
    rows = result.all()
    return {
        "members": [{
            "user_id": row[0].user_id,
            "username": row[1],
            "role": row[0].role,
            "joined_at": row[0].joined_at.isoformat() if row[0].joined_at else None,
        } for row in rows]
    }


@router.get("/{team_id}/dashboard")
async def team_dashboard(team_id: int, user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    # Verify membership
    r = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id, TeamMember.user_id == user.id))
    if not r.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not a team member")

    # Get all team member user_ids
    members_result = await db.execute(
        select(TeamMember.user_id).where(TeamMember.team_id == team_id))
    member_ids = [row[0] for row in members_result.all()]

    # Team test case stats
    tc_count = (await db.execute(
        select(func.count(TestCase.id)).where(TestCase.team_id == team_id)
    )).scalar()

    # Member progress stats
    progress_result = await db.execute(
        select(UserLevelProgress).where(
            UserLevelProgress.user_id.in_(member_ids),
            UserLevelProgress.status == "completed"
        ))
    completed = progress_result.scalars().all()

    # Per-member completion counts
    per_member = {}
    for p in completed:
        per_member[p.user_id] = per_member.get(p.user_id, 0) + 1

    return {
        "team_id": team_id,
        "member_count": len(member_ids),
        "test_case_count": tc_count,
        "member_progress": [{"user_id": uid, "completed": cnt} for uid, cnt in per_member.items()],
    }
