"""delete_account child-row cleanup tests (QA-2026-08-18 HIGH #5)."""
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text, select

from app.database import async_session, sync_engine, init_db, Base
from app.main import app
from app.models.achievement import UserAchievement
from app.models.level import UserLevelProgress
from app.models.test_case import TestCase
from app.models.test_run import TestRun
from app.models.user import User
from app.seed import seed


@pytest.fixture(autouse=True)
def setup():
    Base.metadata.drop_all(sync_engine)
    init_db()
    seed()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def auth(client):
    r = await client.post("/api/auth/register", json={
        "username": "deluser", "email": "del@t.com", "password": "pass1234"
    })
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _seed_children(username: str):
    async with async_session() as db:
        user = (await db.execute(select(User).where(User.username == username))).scalar_one()
        tc = TestCase(user_id=user.id, title="t", steps="s", expected_result="e")
        db.add(tc)
        await db.flush()
        db.add(TestRun(user_id=user.id, test_case_id=tc.id, status="passed"))
        db.add(UserLevelProgress(user_id=user.id, level_id=1, status="in_progress"))
        db.add(UserAchievement(user_id=user.id, achievement_key="first_lab"))
        await db.commit()
        return user.id


@pytest.mark.asyncio
async def test_delete_account_removes_child_rows(client, auth):
    user_id = await _seed_children("deluser")

    r = await client.request("DELETE", "/api/auth/me", json={"password": "pass1234"}, headers=auth)
    assert r.status_code == 200, r.text

    async with async_session() as db:
        assert (await db.execute(select(User).where(User.id == user_id))).first() is None
        assert (await db.execute(select(TestCase).where(TestCase.user_id == user_id))).first() is None
        assert (await db.execute(select(TestRun).where(TestRun.user_id == user_id))).first() is None
        assert (await db.execute(select(UserLevelProgress).where(UserLevelProgress.user_id == user_id))).first() is None
        assert (await db.execute(select(UserAchievement).where(UserAchievement.user_id == user_id))).first() is None


def test_sqlite_foreign_keys_pragma_enabled():
    with sync_engine.connect() as conn:
        assert conn.execute(text("PRAGMA foreign_keys")).scalar() == 1
