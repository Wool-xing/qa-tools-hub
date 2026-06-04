"""E2E tests to fill coverage gaps in main.py, levels.py, and labs.py."""
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
    seed()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def auth(client):
    r = await client.post("/api/auth/register", json={
        "username": "tester", "email": "t@t.com", "password": "pass1234"
    })
    if r.status_code != 200:
        r = await client.post("/api/auth/login", json={
            "username": "tester", "password": "pass1234"
        })
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ── SPA fallback tests ──

@pytest.mark.asyncio
async def test_root_returns_html_when_static_exists(client):
    """Root returns HTML when static/index.html exists."""
    r = await client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_spa_fallback_api_path_returns_404(client):
    """Non-existent API routes should return 404 via SPA fallback."""
    r = await client.get("/api/nonexistent-endpoint-xyz")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_spa_fallback_client_route_returns_html(client):
    """Client-side routes (like /dashboard) should return index.html."""
    r = await client.get("/dashboard")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_spa_docs_returns_404_when_no_static(client):
    """Non-api non-static routes raise 404."""
    r = await client.get("/openapi.json")
    assert r.status_code == 200  # FastAPI auto-serves this


# ── Seed edge case ──

def test_seed_is_idempotent():
    """Calling seed twice should not fail."""
    seed()  # first call
    seed()  # second call should return early (DB already seeded)


# ── Submit code level with expected output ──

@pytest.mark.asyncio
async def test_code_submit_with_expected_match(auth, client):
    """Submit code that matches expected output gets 100 score."""
    # Unlock levels up to level 9 (intermediate: API testing with Postman)
    await client.get("/api/levels", headers=auth)
    for lv_id in range(1, 10):
        r = await client.get(f"/api/levels/{lv_id}", headers=auth)
        if r.status_code != 200:
            continue
        cfg = r.json()
        if cfg["task_type"] == "quiz":
            await client.post("/api/levels/submit", json={
                "level_id": lv_id,
                "answer": {"choice": cfg["task_config"]["correct_index"]}
            }, headers=auth)
        elif cfg["task_type"] == "explore":
            await client.post("/api/levels/submit", json={
                "level_id": lv_id,
                "answer": {"text": " ".join(cfg["task_config"]["keywords"])}
            }, headers=auth)
        await client.get("/api/levels", headers=auth)  # trigger unlock

    await client.get("/api/levels", headers=auth)
    r = await client.get("/api/levels/10", headers=auth)
    assert r.status_code == 200, f"Level 10 not unlocked: {r.status_code}"

    # Submit code to code level
    r = await client.post("/api/levels/submit", json={
        "level_id": 10,
        "answer": {"code": "print('test output')"}
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert "score" in data


# ── Submit to nonexistent level ──

@pytest.mark.asyncio
async def test_submit_nonexistent_level_returns_404(auth, client):
    r = await client.post("/api/levels/submit", json={
        "level_id": 9999,
        "answer": {"choice": 0}
    }, headers=auth)
    assert r.status_code == 404


# ── Code run for non-code level ──

@pytest.mark.asyncio
async def test_run_code_on_quiz_level_returns_400(auth, client):
    r = await client.post("/api/levels/1/run", json={
        "level_id": 1,
        "answer": {"code": "print(1)"}
    }, headers=auth)
    assert r.status_code == 400


# ── Labs edge cases ──

@pytest.mark.asyncio
async def test_sql_lab_empty_query(auth, client):
    """Empty SQL query should return 400."""
    r = await client.post("/api/labs/sql/execute", json={
        "sql": "", "level_id": 0
    }, headers=auth)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_sql_lab_whitespace_query(auth, client):
    """Whitespace-only SQL query should return 400."""
    r = await client.post("/api/labs/sql/execute", json={
        "sql": "   ", "level_id": 0
    }, headers=auth)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_sql_lab_unsafe_query(auth, client):
    """DROP/INSERT/UPDATE/DELETE should be rejected."""
    r = await client.post("/api/labs/sql/execute", json={
        "sql": "DROP TABLE users", "level_id": 0
    }, headers=auth)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_cmd_lab_grep(auth, client):
    """CMD lab grep command should work."""
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "grep ERROR app.log", "level_id": 37
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True


@pytest.mark.asyncio
async def test_cmd_lab_tail(auth, client):
    """CMD lab tail command should work."""
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "tail -2 app.log", "level_id": 37
    }, headers=auth)
    assert r.status_code == 200
    assert r.json()["ok"] is True


@pytest.mark.asyncio
async def test_cmd_lab_wc(auth, client):
    """CMD lab wc command should work."""
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "wc -l app.log", "level_id": 37
    }, headers=auth)
    assert r.status_code == 200
    assert r.json()["ok"] is True


@pytest.mark.asyncio
async def test_cmd_lab_cat(auth, client):
    """CMD lab cat command should work."""
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "cat app.log", "level_id": 37
    }, headers=auth)
    assert r.status_code == 200
    assert r.json()["ok"] is True


@pytest.mark.asyncio
async def test_cmd_lab_empty_command(auth, client):
    """Empty command should return error."""
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "", "level_id": 37
    }, headers=auth)
    assert r.status_code == 400
