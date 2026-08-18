import html as html_mod
import re as _re
import sqlite3
import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.routers.levels import _check_achievements
from app.config import SQL_ROW_LIMIT, PERF_VUS_MAX, PERF_DURATION_MAX
from app.lab_data import (
    SQL_SCENARIOS, is_safe_sql, VFS, resolve_path,
    sim_grep, sim_awk, sim_sort, sim_uniq,
)

# ==================== API Mocking & Service Virtualization ====================

mock_store: dict[str, dict] = {}  # key: "METHOD:/path", value: config
mock_call_counts: dict[str, list[dict]] = {}

class MockCreateRequest(BaseModel):
    method: str = "GET"
    path: str = "/api/test"
    status_code: int = 200
    response_body: str = '{"ok": true}'
    delay_ms: int = 0  # capped at MOCK_MAX_DELAY_MS to prevent DoS via multi-hour sleeps
    sequence: list[dict] = []  # [{order: 1, status: 503, body: 'error', delay: 0}, ...]


MOCK_MAX_DELAY_MS = 10_000

router = APIRouter(prefix="/api/labs", tags=["labs"])


class SQLQuery(BaseModel):
    sql: str
    level_id: int = 0


class CmdQuery(BaseModel):
    cmd: str
    level_id: int = 0


# Commands that read from the virtual filesystem
FILE_COMMANDS = {"cat", "tail", "head", "grep", "sort", "uniq", "wc", "awk", "cut"}


# ==================== SQL Sandbox ====================

@router.post("/sql/execute")
async def execute_sql(data: SQLQuery, user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    from sqlalchemy import update as sa_update
    # Count only VALID visits: increment after input validation, not before
    # (empty/invalid submissions were inflating lab stats, QA-2026-08-18 MEDIUM).
    if not data.sql or not data.sql.strip():
        raise HTTPException(status_code=400, detail="SQL query is required")
    if not is_safe_sql(data.sql):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed in sandbox")

    await db.execute(sa_update(User).where(User.id == user.id).values(lab_visit_count=User.lab_visit_count + 1))
    await db.commit()

    scenario = SQL_SCENARIOS.get(data.level_id, SQL_SCENARIOS["default"])

    try:
        with sqlite3.connect(":memory:") as conn:
            conn.row_factory = sqlite3.Row
            for stmt in scenario["setup"]:
                conn.execute(stmt)
            conn.commit()

            cur = conn.execute(data.sql)
            rows = [dict(r) for r in cur.fetchmany(SQL_ROW_LIMIT)]
            columns = [d[0] for d in cur.description] if cur.description else []
            new_ach = await _check_achievements(user.id, db)
            if new_ach: await db.commit()
            return {"ok": True, "columns": columns, "rows": rows, "row_count": len(rows),
                    "description": scenario["description"], "new_achievements": new_ach}
    except Exception as e:
        import logging
        logging.getLogger("qa-tools").warning("SQL sandbox error: %s", e)
        raise HTTPException(status_code=400, detail="SQL execution failed — check your query syntax")


# ==================== Command Simulator ====================

@router.post("/cmd/execute")
async def execute_cmd(data: CmdQuery, user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    from sqlalchemy import update as sa_update
    cmd = data.cmd.strip()
    if not cmd:
        raise HTTPException(status_code=400, detail="Command is required")
    # Count only VALID visits (QA-2026-08-18 MEDIUM).
    await db.execute(sa_update(User).where(User.id == user.id).values(lab_visit_count=User.lab_visit_count + 1))
    await db.commit()

    parts = cmd.split()
    command = parts[0]
    args = parts[1:] if len(parts) > 1 else []

    file_content = ""
    file_path = ""
    pattern = ""
    flags = ""
    remaining_args = []

    for arg in args:
        if arg.startswith('-') and not arg.startswith('--'):
            flags += arg[1:]
        elif arg in VFS or any(k.endswith(arg) for k in VFS):
            file_path = resolve_path(arg)
            file_content = VFS.get(file_path, "")
        elif not pattern and command in ('grep',):
            pattern = arg
        else:
            remaining_args.append(arg)

    if not file_content and args:
        last = args[-1]
        if not last.startswith('-') and not pattern:
            file_path = resolve_path(last)
            file_content = VFS.get(file_path, "")

    if not file_content:
        # A missing requested file must be reported as such — silently
        # substituting app.log masks the failure (QA-2026-08-18 MEDIUM).
        # Only for commands that actually read the file; unknown commands
        # keep their teaching response below.
        if command in FILE_COMMANDS and file_path:
            return {"ok": False, "error": f"File not found: {file_path}"}
        file_content = VFS.get("/var/log/app.log", "")
        file_path = "/var/log/app.log"

    if command == 'grep' and not pattern and remaining_args:
        pattern = remaining_args[0]

    try:
        if command == 'cat':
            lines = file_content.split('\n')
            n = None
            if 'n' in flags:
                for r in remaining_args:
                    try:
                        n = int(r)
                        break
                    except ValueError:
                        pass
            result = '\n'.join(lines[:n]) if n else file_content
        elif command == 'tail':
            n = 10
            for i, a in enumerate(args):
                if a.startswith('-n'):
                    if len(a) > 2:
                        n = int(a[2:])
                    elif i + 1 < len(args):
                        n = int(args[i + 1])
                elif a.startswith('-') and a[1:].isdigit():
                    n = int(a[1:])
            lines = file_content.split('\n')
            result = '\n'.join(lines[-n:])
        elif command == 'head':
            n = 10
            for i, a in enumerate(args):
                if a.startswith('-n'):
                    if len(a) > 2:
                        n = int(a[2:])
                    elif i + 1 < len(args):
                        n = int(args[i + 1])
                elif a.startswith('-') and a[1:].isdigit():
                    n = int(a[1:])
            lines = file_content.split('\n')
            result = '\n'.join(lines[:n])
        elif command == 'wc':
            lines = file_content.split('\n')
            if 'l' in flags:
                result = str(len(lines))
            elif 'w' in flags:
                result = str(len(file_content.split()))
            else:
                result = f"{len(lines)} {len(file_content.split())} {len(file_content.encode())}"
        elif command == 'grep':
            if not pattern:
                for a in args:
                    if not a.startswith('-') and a not in VFS and not any(a in k for k in VFS):
                        pattern = a
                        break
            if not pattern:
                raise HTTPException(status_code=400, detail="grep requires a pattern")
            result = sim_grep(pattern, file_content, flags)
        elif command == 'sort':
            result = sim_sort(file_content, flags)
        elif command == 'uniq':
            result = sim_uniq(file_content, flags)
        elif command == 'awk':
            script = args[0] if args else '{print}'
            result = sim_awk(script, file_content)
        elif command == 'cut':
            delimiter = '\t'
            field = 1
            for i, a in enumerate(args):
                if a == '-d' and i + 1 < len(args):
                    delimiter = args[i + 1]
                if a.startswith('-f'):
                    try:
                        field = int(a[2:])
                    except ValueError:
                        pass
            lines = file_content.split('\n')
            out = []
            for line in lines:
                parts = line.split(delimiter)
                if field - 1 < len(parts):
                    out.append(parts[field - 1])
            result = '\n'.join(out)
        elif command == 'ls':
            result = '\n'.join(VFS.keys())
        elif command == 'pwd':
            result = '/var/log'
        else:
            result = f"Command '{command}' not supported in sandbox.\nSupported: cat, tail, head, grep, sort, uniq, wc, awk, cut, ls, pwd"

        new_ach = await _check_achievements(user.id, db)
        if new_ach: await db.commit()
        return {"ok": True, "output": result, "file": file_path, "new_achievements": new_ach}
    except HTTPException:
        raise
    except Exception as e:
        # Never leak internal exception text (paths/state) to the client;
        # log server-side for diagnosis (QA-2026-08-18 MEDIUM).
        logging.getLogger("qa-tools").exception("cmd execute internal error user_id=%s", user.id)
        return {"ok": False, "error": "Internal error during command execution"}


# ==================== Security Lab (intentionally vulnerable for training) ====================

# Simulated user database for SQL injection exercises
_SECURITY_USERS = [
    {"id": 1, "username": "admin", "password": "s3cr3t!@#", "role": "admin"},
    {"id": 2, "username": "alice", "password": "password123", "role": "user"},
    {"id": 3, "username": "bob", "password": "qwerty", "role": "user"},
]

_MOCK_BUGS = [
    {"id": 1, "title": "Login crash", "module": "auth", "severity": "P0"},
    {"id": 2, "title": "Data display error", "module": "dashboard", "severity": "P1"},
    {"id": 3, "title": "Export timeout", "module": "report", "severity": "P1"},
]


class SecurityXSSPayload(BaseModel):
    payload: str


class SecuritySQLIPayload(BaseModel):
    username: str
    password: str


@router.post("/security/xss")
async def security_xss(data: SecurityXSSPayload, user: User = Depends(get_current_user)):
    raw = data.payload
    escaped = html_mod.escape(raw)
    script_executed = bool(_re.search(r'<script[^>]*>', raw, _re.IGNORECASE))
    return {
        "payload": raw,
        "escaped": escaped,
        "unsafe_html": f'<div class="search-result">搜索 "{raw}" 的结果：未找到匹配项</div>',
        "safe_html": f'<div class="search-result">搜索 "{escaped}" 的结果：未找到匹配项</div>',
        "script_executed": script_executed,
        "hint": "XSS payload executed!" if script_executed else "Payload was escaped and harmless",
    }


@router.post("/security/sqli")
async def security_sqli(data: SecuritySQLIPayload, user: User = Depends(get_current_user)):
    # Vulnerable query (for training — does NOT execute against real DB)
    vulnerable_query = f"SELECT * FROM users WHERE username='{data.username}' AND password='{data.password}'"
    found = [u for u in _SECURITY_USERS if u["username"] == data.username and u["password"] == data.password]

    # Detect common SQL injection patterns
    injection_patterns = [
        ("' OR ", "OR injection — 永真条件绕过"),
        ("' UNION ", "UNION injection — 联合查询注入"),
        ("' --", "Comment injection — 注释绕过密码检查"),
        ("' #", "Comment injection — 注释绕过密码检查"),
        ("admin'--", "Auth bypass — 管理员账户绕过"),
        ("' OR 1=1", "Classic OR 1=1 — 永恒真值绕过"),
    ]

    detected = []
    for pattern, desc in injection_patterns:
        if pattern.lower() in data.username.lower() or pattern.lower() in data.password.lower():
            detected.append({"pattern": pattern, "description": desc})

    bypassed = not found and len(detected) > 0
    return {
        "vulnerable_query": vulnerable_query,
        "matched_user": found[0] if found else None,
        "injection_detected": len(detected) > 0,
        "injection_types": detected,
        "auth_bypassed": bypassed,
        "secure_query": "SELECT * FROM users WHERE username=? AND password=?  -- 参数化查询防御",
        "lesson": "Always use parameterized queries / ORM. Never concatenate user input into SQL.",
    }


# ==================== Performance / Load Testing Lab ====================


class PerformanceSimRequest(BaseModel):
    script: str
    vus: int = 20
    duration: int = 60


@router.post("/performance/simulate")
async def performance_simulate(data: PerformanceSimRequest, user: User = Depends(get_current_user)):
    if not data.script or not data.script.strip():
        raise HTTPException(status_code=400, detail="k6 script is required")
    if data.vus < 1 or data.vus > PERF_VUS_MAX:
        raise HTTPException(status_code=400, detail=f"VUs must be between 1 and {PERF_VUS_MAX}")
    if data.duration < 10 or data.duration > PERF_DURATION_MAX:
        raise HTTPException(status_code=400, detail=f"Duration must be between 10 and {PERF_DURATION_MAX} seconds")

    from app.lab_data import simulate_k6_run
    # to_thread: pure CPU loop up to PERF_DURATION_MAX (QA-2026-08-18 HIGH #6)
    result = await asyncio.to_thread(simulate_k6_run, data.script, data.vus, data.duration)
    return result


@router.post("/mock/create")
async def mock_create(data: MockCreateRequest, user: User = Depends(get_current_user)):
    key = f"{data.method.upper()}:{data.path.lstrip('/')}"
    if data.delay_ms < 0 or data.delay_ms > MOCK_MAX_DELAY_MS:
        raise HTTPException(status_code=422, detail=f"delay_ms must be between 0 and {MOCK_MAX_DELAY_MS}")
    # Ownership isolation: a mock belongs to its creator. Overwrite only by
    # the owner or an admin (QA-2026-08-18 MEDIUM).
    existing = mock_store.get(key)
    if existing and not user.is_admin and existing.get("owner_id") != user.id:
        raise HTTPException(status_code=409, detail="Mock already registered by another user")
    mock_store[key] = {
        "owner_id": user.id,
        "status_code": data.status_code,
        "response_body": data.response_body,
        "delay_ms": data.delay_ms,
        "sequence": data.sequence,
    }
    mock_call_counts[key] = []
    return {"ok": True, "key": key}


@router.post("/mock/reset")
async def mock_reset(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    mock_store.clear()
    mock_call_counts.clear()
    return {"ok": True}


@router.get("/mock/stats")
async def mock_stats(user: User = Depends(get_current_user)):
    return {"mocks": list(mock_store.keys()), "call_counts": {k: len(v) for k, v in mock_call_counts.items()}}
