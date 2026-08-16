"""TDD tests for fixes made during code review — these would have caught the bugs."""
import os
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db, sync_engine, Base
from app.seed import seed


@pytest.fixture(autouse=True)
def setup():
    Base.metadata.drop_all(sync_engine)
    init_db()


# ==================== Fix: seed works without DATABASE_URL env var ====================

def test_seed_runs_without_env_var(monkeypatch):
    """Seed should run even when DATABASE_URL env var is not set."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SEED_DB", raising=False)
    init_db()
    seed()
    from sqlalchemy import text
    with sync_engine.connect() as conn:
        r = conn.execute(text("SELECT count(*) FROM levels"))
        assert r.scalar() > 0, "Seed should populate levels"


def test_seed_respects_config_url():
    """Seed should use app.config.DATABASE_URL, not os.getenv directly.

    This test verifies the fix where seed() was changed from
    os.getenv('DATABASE_URL') to app.config.DATABASE_URL.
    With the default config (sqlite), seed should run successfully.
    """
    init_db()
    seed()
    from sqlalchemy import text
    with sync_engine.connect() as conn:
        r = conn.execute(text("SELECT count(*) FROM levels"))
        assert r.scalar() > 0


def test_seed_runs_non_sqlite_with_flag(monkeypatch):
    """Seed should run on non-SQLite when SEED_DB=true."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/test")
    monkeypatch.setenv("SEED_DB", "true")
    init_db()
    seed()
    from sqlalchemy import text
    with sync_engine.connect() as conn:
        r = conn.execute(text("SELECT count(*) FROM levels"))
        assert r.scalar() > 0, "Seed should run with SEED_DB flag"


# ==================== Fix: alembic migration runs at startup ====================

def test_startup_db_schema_matches_models():
    """After init_db + seed, all model columns should exist in DB tables."""
    init_db()
    seed()
    from sqlalchemy import inspect
    inspector = inspect(sync_engine)
    columns = {c["name"] for c in inspector.get_columns("test_cases")}
    assert "team_id" in columns, "test_cases should have team_id column"
    assert "level_id" in columns, "test_cases should have level_id column"
    assert "tags" in columns, "test_cases should have tags column"
    assert "folder" in columns, "test_cases should have folder column"


# ==================== Fix: reset-password rate limiting ====================

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_reset_password_rate_limit_triggers(client):
    """Rate limit should trigger on 6th reset-password call."""
    from app.routers.auth import reset_rate_limits
    reset_rate_limits()
    last_status = None
    for _ in range(7):
        r = await client.post("/api/auth/reset-password", json={
            "token": "bad-token", "new_password": "pass1234"
        })
        last_status = r.status_code
    assert last_status == 429, f"Expected 429, got {last_status}"


@pytest.mark.asyncio
async def test_reset_password_rate_limit_429_response(client):
    """Rate limit should return 429 with proper status code."""
    from app.routers.auth import reset_rate_limits
    reset_rate_limits()
    last_r = None
    for _ in range(7):
        last_r = await client.post("/api/auth/reset-password", json={
            "token": "bad-token", "new_password": "pass1234"
        })
    assert last_r.status_code == 429
    assert "Too many requests" in last_r.json()["detail"]


# ==================== Fix: reset token stored as SHA-256 hash ====================

def test_reset_token_stored_as_hash():
    """Reset tokens in DB should be SHA-256 hex, not plaintext."""
    import secrets, hashlib
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    # SHA-256 produces exactly 64 hex characters
    assert len(token_hash) == 64
    assert all(c in "0123456789abcdef" for c in token_hash)
    # It should NOT look like a base64 token (no - or _)
    assert "-" not in token_hash and "_" not in token_hash


# ==================== Fix: token revoked after password change ====================

@pytest.mark.asyncio
async def test_token_revoked_after_password_change(client):
    """After changing password, old token should be rejected."""
    from app.routers.auth import reset_rate_limits, reset_token_blacklist
    reset_rate_limits()
    reset_token_blacklist()

    r = await client.post("/api/auth/register", json={
        "username": "pwtest", "email": "pwtest@t.com", "password": "oldpw123"
    })
    assert r.status_code == 200
    old_token = r.json()["access_token"]
    old_headers = {"Authorization": f"Bearer {old_token}"}

    r = await client.patch("/api/auth/me", json={
        "current_password": "oldpw123", "new_password": "newpw456"
    }, headers=old_headers)
    assert r.status_code == 200

    r = await client.get("/api/auth/me", headers=old_headers)
    assert r.status_code == 401, "Old token should be revoked"
