"""Unit tests for labs router"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db, sync_engine, Base
from app.seed import seed
from app.lab_data import is_safe_sql, sim_grep, sim_awk, sim_sort, sim_uniq, resolve_path, VFS


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
        "username": "labtester", "email": "lab@t.com", "password": "pass1234"
    })
    if r.status_code != 200:
        r = await client.post("/api/auth/login", json={
            "username": "labtester", "password": "pass1234"
        })
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ==================== SQL Safety ====================

def test_is_safe_sql_select():
    assert is_safe_sql("SELECT * FROM users")
    assert is_safe_sql("select name, count(*) from bugs group by name")


def test_is_safe_sql_rejects_drop():
    assert not is_safe_sql("DROP TABLE users")
    assert not is_safe_sql("drop table users")


def test_is_safe_sql_rejects_insert():
    assert not is_safe_sql("INSERT INTO users VALUES (1)")


def test_is_safe_sql_rejects_delete():
    assert not is_safe_sql("DELETE FROM users")


def test_is_safe_sql_rejects_update():
    assert not is_safe_sql("UPDATE users SET name='x'")


def test_is_safe_sql_rejects_create():
    assert not is_safe_sql("CREATE TABLE x (id INT)")


def test_is_safe_sql_rejects_alter():
    assert not is_safe_sql("ALTER TABLE users ADD COLUMN x")


# ==================== SQL Sandbox API ====================

@pytest.mark.asyncio
async def test_sql_empty_query(auth, client):
    r = await client.post("/api/labs/sql/execute", json={
        "sql": "", "level_id": 0
    }, headers=auth)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_sql_select_all(auth, client):
    r = await client.post("/api/labs/sql/execute", json={
        "sql": "SELECT * FROM test_data", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert len(data["rows"]) == 5


@pytest.mark.asyncio
async def test_sql_select_columns(auth, client):
    r = await client.post("/api/labs/sql/execute", json={
        "sql": "SELECT name, value FROM test_data WHERE category = 'B'",
        "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["columns"] == ["name", "value"]
    assert len(data["rows"]) == 2


@pytest.mark.asyncio
async def test_sql_select_aggregate(auth, client):
    r = await client.post("/api/labs/sql/execute", json={
        "sql": "SELECT category, COUNT(*), SUM(value) FROM test_data GROUP BY category",
        "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True


@pytest.mark.asyncio
async def test_sql_scenario_bugs(auth, client):
    r = await client.post("/api/labs/sql/execute", json={
        "sql": "SELECT severity, COUNT(*) as cnt FROM bugs GROUP BY severity ORDER BY cnt DESC",
        "level_id": 38
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert len(data["rows"]) > 0


@pytest.mark.asyncio
async def test_sql_syntax_error(auth, client):
    r = await client.post("/api/labs/sql/execute", json={
        "sql": "SELECTT * FROM test_data", "level_id": 0
    }, headers=auth)
    assert r.status_code == 400
    data = r.json()
    assert "detail" in data


# ==================== Command Simulator (unit) ====================

def test_sim_grep_basic():
    result = sim_grep("ERROR", VFS["/var/log/app.log"])
    assert "ERROR" in result
    assert len(result.split('\n')) == 5


def test_sim_grep_case_insensitive():
    result = sim_grep("error", VFS["/var/log/app.log"], flags="i")
    assert len(result.split('\n')) == 5


def test_sim_grep_count():
    result = sim_grep("ERROR", VFS["/var/log/app.log"], flags="c")
    assert result == "5"


def test_sim_grep_invert():
    result = sim_grep("ERROR", VFS["/var/log/app.log"], flags="v")
    assert "ERROR" not in result


def test_sim_awk_basic():
    content = "a b c\n1 2 3"
    result = sim_awk("{print $1}", content)
    assert result == "a\n1"


def test_sim_awk_two_fields():
    content = "192.168.1.1 - - [date]"
    result = sim_awk("{print $1, $2}", content)
    assert "192.168.1.1 -" in result


def test_sim_sort_alphabetical():
    content = "z\na\nm"
    result = sim_sort(content)
    assert result == "a\nm\nz"


def test_sim_sort_reverse():
    content = "a\nc\nb"
    result = sim_sort(content, flags="r")
    assert result == "c\nb\na"


def test_sim_uniq_basic():
    content = "a\na\nb"
    result = sim_uniq(content)
    assert result == "a\nb"


def test_sim_uniq_count():
    content = "a\na\nb"
    result = sim_uniq(content, flags="c")
    assert "2 a" in result
    assert "1 b" in result


def test_resolve_path_exact():
    assert resolve_path("/var/log/app.log") == "/var/log/app.log"


def test_resolve_path_not_found():
    result = resolve_path("/nonexistent/path")
    assert result == "/nonexistent/path"


# ==================== Command Simulator API ====================

@pytest.mark.asyncio
async def test_cmd_cat(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "cat /var/log/app.log", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "Server started" in data["output"]


@pytest.mark.asyncio
async def test_cmd_head(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "head -n 2 /var/log/app.log", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert len(data["output"].split('\n')) == 2


@pytest.mark.asyncio
async def test_cmd_grep_count(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "grep -c ERROR /var/log/app.log", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["output"] == "5"


@pytest.mark.asyncio
async def test_cmd_grep_invert(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "grep -v ERROR /var/log/app.log", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "ERROR" not in data["output"]


@pytest.mark.asyncio
async def test_cmd_wc_words(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "wc -w /var/log/app.log", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert int(data["output"]) > 0


@pytest.mark.asyncio
async def test_cmd_cut(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "cut -d ' ' -f 1 /etc/hosts", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "127.0.0.1" in data["output"]


@pytest.mark.asyncio
async def test_cmd_sort_reverse(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "sort -r /etc/hosts", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True


@pytest.mark.asyncio
async def test_cmd_invalid_command(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "sudo rm -rf /", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "not supported" in data["output"]


@pytest.mark.asyncio
async def test_cmd_empty(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "", "level_id": 0
    }, headers=auth)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_cmd_defaults_to_app_log(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "cat", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "Server started" in data["output"]


# ==================== CMD coverage: remaining variants ====================

@pytest.mark.asyncio
async def test_cmd_tail_dash_n_combined(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "tail -n3 /var/log/app.log", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert len(r.json()["output"].split('\n')) == 3


@pytest.mark.asyncio
async def test_cmd_tail_dash_number(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "tail -3 /var/log/app.log", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert len(r.json()["output"].split('\n')) == 3


@pytest.mark.asyncio
async def test_cmd_head_dash_n_combined(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "head -n2 /var/log/app.log", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert len(r.json()["output"].split('\n')) == 2


@pytest.mark.asyncio
async def test_cmd_head_dash_number(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "head -2 /var/log/app.log", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert len(r.json()["output"].split('\n')) == 2


@pytest.mark.asyncio
async def test_cmd_cat_dash_n(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "cat -n 3 /var/log/app.log", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert len(r.json()["output"].split('\n')) == 3


@pytest.mark.asyncio
async def test_cmd_wc_default(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "wc /var/log/app.log", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    # Output should have 3 numbers: lines words bytes
    parts = data["output"].split()
    assert len(parts) == 3


@pytest.mark.asyncio
async def test_cmd_cut_delimiter(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "cut -d . -f 1 /etc/hosts", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    assert r.json()["ok"] is True


@pytest.mark.asyncio
async def test_cmd_sort_numeric(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "sort -n /etc/hosts", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    assert r.json()["ok"] is True


@pytest.mark.asyncio
async def test_cmd_grep_without_pattern(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "grep /var/log/app.log", "level_id": 0
    }, headers=auth)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_cmd_pipe_separated_args(auth, client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "cat -n 5 /etc/hosts", "level_id": 0
    }, headers=auth)
    assert r.status_code == 200
    assert r.json()["ok"] is True


@pytest.mark.asyncio
async def test_resolve_path_by_tail_match():
    assert resolve_path("app.log") == "/var/log/app.log"


@pytest.mark.asyncio
async def test_resolve_path_no_match():
    assert resolve_path("nonexistent.log") == "nonexistent.log"


# ==================== Auth required ====================

@pytest.mark.asyncio
async def test_sql_lab_requires_auth(client):
    r = await client.post("/api/labs/sql/execute", json={
        "sql": "SELECT 1", "level_id": 0
    })
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_cmd_lab_requires_auth(client):
    r = await client.post("/api/labs/cmd/execute", json={
        "cmd": "ls", "level_id": 0
    })
    assert r.status_code == 401


# ==================== Performance Lab ====================

@pytest.mark.asyncio
async def test_performance_simulate_basic(auth, client):
    r = await client.post("/api/labs/performance/simulate", json={
        "script": "import http from 'k6/http';\nexport default function() { http.get('http://test.k6.io'); }",
        "vus": 10,
        "duration": 30
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "latency" in data
    assert "p50" in data["latency"]
    assert "p95" in data["latency"]
    assert "p99" in data["latency"]
    assert data["latency"]["p50"] <= data["latency"]["p95"] <= data["latency"]["p99"]
    assert "throughput" in data
    assert data["throughput"]["avg_rps"] > 0
    assert "per_second" in data
    assert data["duration_sec"] == 30


@pytest.mark.asyncio
async def test_performance_simulate_empty_script(auth, client):
    r = await client.post("/api/labs/performance/simulate", json={
        "script": "", "vus": 10, "duration": 30
    }, headers=auth)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_performance_simulate_vus_limit(auth, client):
    r = await client.post("/api/labs/performance/simulate", json={
        "script": "http.get('http://x');", "vus": 1000, "duration": 30
    }, headers=auth)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_performance_simulate_duration_limit(auth, client):
    r = await client.post("/api/labs/performance/simulate", json={
        "script": "http.get('http://x');", "vus": 10, "duration": 5
    }, headers=auth)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_performance_simulate_with_ramp(auth, client):
    r = await client.post("/api/labs/performance/simulate", json={
        "script": "import http from 'k6/http';\nexport const options = { stages: [{ duration: '30s', target: 20 }] };\nexport default function() { http.get('http://test.k6.io'); }",
        "vus": 50,
        "duration": 60
    }, headers=auth)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert "error_rate" in data
    rps_values = [s["rps"] for s in data["per_second"]]
    assert rps_values[0] < rps_values[-10]


@pytest.mark.asyncio
async def test_performance_lab_requires_auth(client):
    r = await client.post("/api/labs/performance/simulate", json={
        "script": "http.get('http://x');", "vus": 10, "duration": 30
    })
    assert r.status_code == 401
