"""E2E tests for QA通关 Pro API"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db, sync_engine, Base
from app.seed import seed


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(sync_engine)
    init_db()
    seed()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def auth_headers(client):
    r = await client.post("/api/auth/register", json={
        "username": "e2e_user", "email": "e2e@test.com", "password": "testpass1"
    })
    if r.status_code != 200:
        r = await client.post("/api/auth/login", json={
            "username": "e2e_user", "password": "testpass1"
        })
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ==================== Root ====================

@pytest.mark.asyncio
async def test_root_returns_frontend(client):
    r = await client.get("/")
    assert r.status_code == 200
    # Returns HTML when frontend is built, JSON otherwise
    content_type = r.headers.get("content-type", "")
    if "text/html" in content_type:
        assert "DOCTYPE" in r.text.upper()
    else:
        assert "QA通关" in r.json()["message"]


# ==================== Auth ====================

@pytest.mark.asyncio
async def test_register_and_login(client):
    r = await client.post("/api/auth/register", json={
        "username": "tester1", "email": "t1@t.com", "password": "secret123"
    })
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["username"] == "tester1"

    r = await client.post("/api/auth/login", json={
        "username": "tester1", "password": "secret123"
    })
    assert r.status_code == 200
    assert r.json()["username"] == "tester1"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    r = await client.post("/api/auth/login", json={
        "username": "nobody", "password": "wrong"
    })
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_auth_me(auth_headers, client):
    r = await client.get("/api/auth/me", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["username"] == "e2e_user"


@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    r = await client.post("/api/auth/register", json={
        "username": "dup_user", "email": "dup@t.com", "password": "pass1234"
    })
    assert r.status_code == 200
    r = await client.post("/api/auth/register", json={
        "username": "dup_user", "email": "dup2@t.com", "password": "pass4567"
    })
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_invalid_token_rejected(client):
    r = await client.get("/api/auth/me", headers={
        "Authorization": "Bearer invalid-token"
    })
    assert r.status_code == 401


# ==================== Levels ====================

@pytest.mark.asyncio
async def test_list_levels_with_progress(auth_headers, client):
    r = await client.get("/api/levels", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "levels" in data
    assert "stages" in data
    assert "progress" in data
    assert len(data["levels"]) == 102
    assert "beginner" in data["stages"]
    # First level should be unlocked
    first = data["levels"][0]
    assert first["status"] in ("unlocked", "in_progress", "completed")


@pytest.mark.asyncio
async def test_level_requires_auth(client):
    r = await client.get("/api/levels")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_get_level_detail(auth_headers, client):
    await client.get("/api/levels", headers=auth_headers)  # creates progress
    r = await client.get("/api/levels/1", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "什么是软件测试？"
    assert data["task_type"] == "quiz"
    assert "theory" in data


@pytest.mark.asyncio
async def test_submit_quiz_correct(auth_headers, client):
    # list_levels creates initial progress record
    await client.get("/api/levels", headers=auth_headers)
    await client.get("/api/levels/1", headers=auth_headers)
    r = await client.post("/api/levels/submit", json={
        "level_id": 1,
        "answer": {"choice": 1}
    }, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["correct"] is True
    assert data["score"] == 100


@pytest.mark.asyncio
async def test_submit_quiz_wrong(auth_headers, client):
    await client.get("/api/levels", headers=auth_headers)
    await client.get("/api/levels/1", headers=auth_headers)
    r = await client.post("/api/levels/submit", json={
        "level_id": 1,
        "answer": {"choice": 0}
    }, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["correct"] is False
    assert data["score"] == 0


@pytest.mark.asyncio
async def test_submit_explore(auth_headers, client):
    await client.get("/api/levels", headers=auth_headers)
    await client.get("/api/levels/1", headers=auth_headers)
    await client.post("/api/levels/submit", json={
        "level_id": 1, "answer": {"choice": 1}  # correct for level 1
    }, headers=auth_headers)
    # list_levels triggers unlock of next level
    await client.get("/api/levels", headers=auth_headers)
    # Complete level 2 to unlock level 3
    await client.get("/api/levels/2", headers=auth_headers)
    await client.post("/api/levels/submit", json={
        "level_id": 2, "answer": {"choice": 2}  # correct for level 2
    }, headers=auth_headers)
    # list_levels triggers unlock of level 3
    await client.get("/api/levels", headers=auth_headers)
    # Now level 3 (explore) should be unlocked
    await client.get("/api/levels/3", headers=auth_headers)
    r = await client.post("/api/levels/submit", json={
        "level_id": 3,
        "answer": {"text": "需求 评审 尽早 早期 成本 shift left 测试"}
    }, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["score"] > 0


@pytest.mark.asyncio
async def test_run_code_sandbox(auth_headers, client):
    from app.database import sync_engine as se
    from sqlalchemy import text
    me = await client.get("/api/auth/me", headers=auth_headers)
    uid = me.json()["id"]
    with se.begin() as conn:
        conn.execute(text(
            f"INSERT INTO user_level_progress (user_id, level_id, status, score, attempts) "
            f"VALUES ({uid}, 10, 'unlocked', 0, 0)"
        ))
    r = await client.post("/api/levels/10/run", json={
        "level_id": 10,
        "answer": {"code": "print('hello selenium')"}
    }, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "hello selenium" in data["stdout"]


@pytest.mark.asyncio
async def test_level_404(auth_headers, client):
    r = await client.get("/api/levels/999", headers=auth_headers)
    assert r.status_code == 404


# ==================== Labs ====================

@pytest.mark.asyncio
async def test_sql_sandbox_select(auth_headers, client):
    r = await client.post("/api/labs/sql/execute", json={
        "sql": "SELECT * FROM test_data WHERE category = 'A'",
        "level_id": 0
    }, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert len(data["rows"]) == 3
    assert "id" in data["columns"]


@pytest.mark.asyncio
async def test_sql_sandbox_rejects_drop(auth_headers, client):
    r = await client.post("/api/labs/sql/execute", json={
        "sql": "DROP TABLE test_data",
        "level_id": 0
    }, headers=auth_headers)
    assert r.status_code == 400
    assert "Only SELECT" in r.json()["detail"]


@pytest.mark.asyncio
async def test_sql_scenario_level_38(auth_headers, client):
    r = await client.post("/api/labs/sql/execute", json={
        "sql": "SELECT module, COUNT(*) as cnt FROM bugs GROUP BY module ORDER BY cnt DESC",
        "level_id": 38
    }, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert len(data["rows"]) > 0


@pytest.mark.asyncio
async def test_cmd_grep(auth_headers, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "grep ERROR /var/log/app.log",
        "level_id": 0
    }, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "ERROR" in data["output"]


@pytest.mark.asyncio
async def test_cmd_tail(auth_headers, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "tail -n 3 /var/log/app.log",
        "level_id": 0
    }, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert len(data["output"].split('\n')) == 3


@pytest.mark.asyncio
async def test_cmd_wc(auth_headers, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "wc -l /var/log/nginx/access.log",
        "level_id": 0
    }, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["output"] == "10"


@pytest.mark.asyncio
async def test_cmd_sort(auth_headers, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "sort /etc/hosts",
        "level_id": 0
    }, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "localhost" in data["output"]


@pytest.mark.asyncio
async def test_cmd_uniq_count(auth_headers, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "sort /var/log/nginx/access.log | uniq -c",
        "level_id": 0
    }, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True


@pytest.mark.asyncio
async def test_cmd_awk(auth_headers, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "awk {print $1} /var/log/nginx/access.log",
        "level_id": 0
    }, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True


@pytest.mark.asyncio
async def test_cmd_ls(auth_headers, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "ls",
        "level_id": 0
    }, headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "/var/log" in data["output"]


@pytest.mark.asyncio
async def test_labs_require_auth(client):
    r = await client.post("/api/labs/sql/execute", json={
        "sql": "SELECT 1", "level_id": 0
    })
    assert r.status_code == 401


# ==================== Production Features ====================

@pytest.mark.asyncio
async def test_health_endpoint(client):
    r = await client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["service"] == "qa-tools-pro"


@pytest.mark.asyncio
async def test_security_headers(client):
    r = await client.get("/health")
    assert r.headers.get("x-content-type-options") == "nosniff"
    assert r.headers.get("x-frame-options") == "DENY"
    assert r.headers.get("x-request-id")


@pytest.mark.asyncio
async def test_forgot_password_nonexist(client):
    r = await client.post("/api/auth/forgot-password", json={"email": "nonexist@test.com"})
    assert r.status_code == 200
    assert "sent" in r.json()["message"]


@pytest.mark.asyncio
async def test_forgot_password_real_user(client):
    await client.post("/api/auth/register", json={
        "username": "forgotme", "email": "forgot@test.com", "password": "test1234"
    })
    r = await client.post("/api/auth/forgot-password", json={"email": "forgot@test.com"})
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_reset_password_bad_token(client):
    r = await client.post("/api/auth/reset-password", json={
        "token": "invalid-token", "new_password": "newpass123"
    })
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_reset_password_flow(client):
    # Register
    reg = await client.post("/api/auth/register", json={
        "username": "resetflow", "email": "reset@test.com", "password": "oldpass1"
    })
    assert reg.status_code == 200
    token = reg.json()["access_token"]

    # Verify old password works
    login1 = await client.post("/api/auth/login", json={
        "username": "resetflow", "password": "oldpass1"
    })
    assert login1.status_code == 200

    # Check user record for reset_token
    from app.database import sync_engine, SyncSession
    from app.models.user import User
    from sqlalchemy import select
    import secrets
    from datetime import datetime, timedelta, timezone
    import hashlib
    import bcrypt

    with SyncSession() as sess:
        u = sess.execute(select(User).where(User.username == "resetflow")).scalar_one()
        reset_token = secrets.token_urlsafe(32)
        u.reset_token = hashlib.sha256(reset_token.encode()).hexdigest()
        u.reset_token_expires = datetime.now(timezone.utc) + timedelta(minutes=30)
        sess.commit()

    # Reset password
    r = await client.post("/api/auth/reset-password", json={
        "token": reset_token, "new_password": "newpass123"
    })
    assert r.status_code == 200

    # Old password should fail
    login_old = await client.post("/api/auth/login", json={
        "username": "resetflow", "password": "oldpass1"
    })
    assert login_old.status_code == 401

    # New password should work
    login_new = await client.post("/api/auth/login", json={
        "username": "resetflow", "password": "newpass123"
    })
    assert login_new.status_code == 200


@pytest.mark.asyncio
async def test_register_validation_username_short(client):
    r = await client.post("/api/auth/register", json={
        "username": "ab", "email": "test@test.com", "password": "pass1234"
    })
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_register_validation_bad_email(client):
    r = await client.post("/api/auth/register", json={
        "username": "gooduser", "email": "notanemail", "password": "pass1234"
    })
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_register_validation_short_password(client):
    r = await client.post("/api/auth/register", json={
        "username": "gooduser", "email": "a@b.com", "password": "ab"
    })
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_rate_limit_login(client):
    for _ in range(6):
        r = await client.post("/api/auth/login", json={
            "username": "bad", "password": "wrong"
        })
    # 6th should be rate limited
    assert r.status_code == 429


@pytest.mark.asyncio
async def test_rate_limit_reset_password(client):
    for _ in range(6):
        r = await client.post("/api/auth/reset-password", json={
            "token": "bad-token", "new_password": "pass1234"
        })
    # 6th should be rate limited
    assert r.status_code == 429
