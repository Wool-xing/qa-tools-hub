"""Mock store ownership isolation + delay cap tests (QA-2026-08-18 MEDIUM)."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.database import sync_engine, init_db, Base
from app.main import app
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


async def _register(client, name):
    r = await client.post("/api/auth/register", json={
        "username": name, "email": f"{name}@t.com", "password": "pass1234"
    })
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.mark.asyncio
async def test_other_user_cannot_overwrite_mock(client):
    a = await _register(client, "mocka")
    b = await _register(client, "mockb")
    r1 = await client.post("/api/labs/mock/create", json={
        "method": "GET", "path": "/shared", "response_body": '{"from":"a"}'
    }, headers=a)
    assert r1.status_code == 200
    r2 = await client.post("/api/labs/mock/create", json={
        "method": "GET", "path": "/shared", "response_body": '{"from":"b"}'
    }, headers=b)
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_owner_can_overwrite_own_mock(client):
    a = await _register(client, "mockowner")
    r1 = await client.post("/api/labs/mock/create", json={
        "method": "GET", "path": "/own", "response_body": '{"v":1}'
    }, headers=a)
    assert r1.status_code == 200
    r2 = await client.post("/api/labs/mock/create", json={
        "method": "GET", "path": "/own", "response_body": '{"v":2}'
    }, headers=a)
    assert r2.status_code == 200


@pytest.mark.asyncio
async def test_delay_ms_capped(client):
    a = await _register(client, "mockdelay")
    r = await client.post("/api/labs/mock/create", json={
        "method": "GET", "path": "/slow", "delay_ms": 999999
    }, headers=a)
    assert r.status_code == 422
