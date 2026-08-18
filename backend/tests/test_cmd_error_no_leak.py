"""cmd/execute internal errors must not leak internals (QA-2026-08-18 MEDIUM)."""
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.database import async_session, sync_engine, init_db, Base
from app.main import app
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
        "username": "leakuser", "email": "leak@t.com", "password": "pass1234"
    })
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.mark.asyncio
async def test_internal_error_text_not_leaked(client, auth, monkeypatch):
    import app.routers.labs as labs_module

    def _boom(script, content):
        raise RuntimeError("SECRET /etc/passwd internal path C:\\Users\\admin")

    monkeypatch.setattr(labs_module, "sim_awk", _boom)
    r = await client.post("/api/labs/cmd/execute", json={"cmd": "awk"}, headers=auth)
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False
    assert "SECRET" not in body["error"]
    assert "Internal error" in body["error"]
