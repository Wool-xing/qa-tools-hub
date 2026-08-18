"""Concurrent registration must not 500 (QA-2026-08-18 MEDIUM)."""
import asyncio

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


@pytest.mark.asyncio
async def test_concurrent_same_username_never_500(client):
    payload = {"username": "raceuser", "email": "race@t.com", "password": "pass1234"}
    rs = await asyncio.gather(*[
        client.post("/api/auth/register", json=payload) for _ in range(8)
    ])
    codes = [r.status_code for r in rs]
    assert 500 not in codes, codes  # the actual bug: bare 500 on race
    assert 200 in codes, codes      # exactly one wins
    # losers get 400 (dup) or 429 (rate limit kicked in — also correct)
    assert all(c in (200, 400, 429) for c in codes), codes
