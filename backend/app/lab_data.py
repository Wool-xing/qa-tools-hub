"""Lab data: SQL scenarios, virtual filesystem, and command simulators."""

import re
import random
import math
from collections import Counter

# ==================== SQL Sandbox Data ====================

FORBIDDEN_SQL = ["DROP", "ALTER", "CREATE", "INSERT", "UPDATE", "DELETE",
                  "ATTACH", "DETACH", "PRAGMA", "REINDEX", "VACUUM"]

SQL_SCENARIOS = {
    38: {
        "setup": [
            "CREATE TABLE bugs (id INTEGER PRIMARY KEY, title TEXT, module TEXT, severity TEXT, status TEXT, assignee TEXT)",
            "INSERT INTO bugs VALUES (1,'登录页崩溃','login','P0','fixed','Alice')",
            "INSERT INTO bugs VALUES (2,'数据显示错误','dashboard','P1','open','Bob')",
            "INSERT INTO bugs VALUES (3,'导出超时','report','P1','fixed','Alice')",
            "INSERT INTO bugs VALUES (4,'搜索无结果','search','P2','open','Charlie')",
            "INSERT INTO bugs VALUES (5,'权限绕过','auth','P0','open','Bob')",
            "INSERT INTO bugs VALUES (6,'分页Bug','dashboard','P3','fixed','Alice')",
        ],
        "description": "缺陷管理数据库，表bugs: id,title,module,severity,status,assignee",
    },
    31: {
        "setup": [
            "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)",
            "INSERT INTO users VALUES (1,'admin','secret123','admin')",
            "INSERT INTO users VALUES (2,'alice','pass456','user')",
            "INSERT INTO users VALUES (3,'bob','qwerty','user')",
        ],
        "description": "用户表users: id,username,password,role",
    },
    "default": {
        "setup": [
            "CREATE TABLE test_data (id INTEGER PRIMARY KEY, name TEXT, value INTEGER, category TEXT)",
            "INSERT INTO test_data VALUES (1,'alpha',100,'A')",
            "INSERT INTO test_data VALUES (2,'beta',200,'A')",
            "INSERT INTO test_data VALUES (3,'gamma',300,'B')",
            "INSERT INTO test_data VALUES (4,'delta',400,'B')",
            "INSERT INTO test_data VALUES (5,'epsilon',500,'A')",
        ],
        "description": "通用测试数据表test_data: id,name,value,category",
    },
    41: {
        "setup": [
            "CREATE TABLE orders (order_id INTEGER PRIMARY KEY, user_id INTEGER, total REAL, status TEXT)",
            "INSERT INTO orders VALUES (1,1,99.99,'paid')",
            "INSERT INTO orders VALUES (2,2,149.50,'paid')",
            "INSERT INTO orders VALUES (3,1,200.00,'pending')",
            "INSERT INTO orders VALUES (4,3,75.00,'paid')",
            "INSERT INTO orders VALUES (5,2,59.99,'paid')",
            "CREATE TABLE users (user_id INTEGER PRIMARY KEY, name TEXT, email TEXT)",
            "INSERT INTO users VALUES (1,'Alice','alice@test.com')",
            "INSERT INTO users VALUES (2,'Bob','bob@test.com')",
            "INSERT INTO users VALUES (3,'Charlie','charlie@test.com')",
            "CREATE TABLE payments (payment_id INTEGER PRIMARY KEY, order_id INTEGER, amount REAL, method TEXT)",
            "INSERT INTO payments VALUES (1,1,99.99,'credit')",
            "INSERT INTO payments VALUES (2,2,149.50,'debit')",
            "INSERT INTO payments VALUES (3,3,150.00,'credit')",
            "INSERT INTO payments VALUES (4,4,75.00,'credit')",
            "INSERT INTO payments VALUES (5,5,45.00,'debit')",
        ],
        "description": "订单数据库: orders(order_id,user_id,total,status), users(user_id,name,email), payments(payment_id,order_id,amount,method)",
    },
    42: {
        "setup": [
            "CREATE TABLE test_runs (test_id INTEGER, run_date TEXT, status TEXT, duration_sec REAL)",
            "INSERT INTO test_runs VALUES (1,'2024-01-01','pass',1.2)",
            "INSERT INTO test_runs VALUES (1,'2024-01-08','pass',1.5)",
            "INSERT INTO test_runs VALUES (1,'2024-01-15','pass',2.1)",
            "INSERT INTO test_runs VALUES (1,'2024-01-22','pass',3.8)",
            "INSERT INTO test_runs VALUES (2,'2024-01-01','pass',0.8)",
            "INSERT INTO test_runs VALUES (2,'2024-01-08','pass',0.9)",
            "INSERT INTO test_runs VALUES (2,'2024-01-15','pass',0.7)",
            "INSERT INTO test_runs VALUES (2,'2024-01-22','pass',1.0)",
            "INSERT INTO test_runs VALUES (3,'2024-01-01','pass',2.5)",
            "INSERT INTO test_runs VALUES (3,'2024-01-08','pass',3.2)",
            "INSERT INTO test_runs VALUES (3,'2024-01-15','fail',5.1)",
            "INSERT INTO test_runs VALUES (3,'2024-01-22','pass',6.0)",
            "INSERT INTO test_runs VALUES (4,'2024-01-01','pass',0.5)",
            "INSERT INTO test_runs VALUES (4,'2024-01-08','pass',0.6)",
            "INSERT INTO test_runs VALUES (4,'2024-01-15','pass',0.5)",
            "INSERT INTO test_runs VALUES (4,'2024-01-22','pass',0.7)",
        ],
        "description": "测试运行记录: test_runs(test_id,run_date,status,duration_sec). test_id=1和3持续变慢, test_id=2和4稳定.",
    },
    43: {
        "setup": [
            "CREATE TABLE products (product_id INTEGER PRIMARY KEY, name TEXT, price REAL, description TEXT, category TEXT)",
            "INSERT INTO products VALUES (1,'Widget A',19.99,'A useful widget','electronics')",
            "INSERT INTO products VALUES (2,'Widget B',NULL,'Another widget','electronics')",
            "INSERT INTO products VALUES (3,'Gadget X',29.99,NULL,'electronics')",
            "INSERT INTO products VALUES (4,'Gadget Y',NULL,NULL,'electronics')",
            "INSERT INTO products VALUES (5,'Tool Pro',49.99,'Professional tool',NULL)",
            "INSERT INTO products VALUES (6,'Tool Lite',9.99,NULL,NULL)",
            "INSERT INTO products VALUES (7,'Super Widget',NULL,'Premium widget','electronics')",
            "INSERT INTO products VALUES (8,'Mystery Box',NULL,NULL,NULL)",
        ],
        "description": "产品表含NULL: products(product_id,name,price,description,category). price有4个NULL, description有4个NULL, category有3个NULL.",
    },
}


def is_safe_sql(sql: str) -> bool:
    cleaned = re.sub(r'--[^\n]*', '', sql)
    cleaned = re.sub(r'/\*[\s\S]*?\*/', '', cleaned)
    upper = cleaned.upper()
    for kw in FORBIDDEN_SQL:
        if re.search(r'\b' + kw + r'\b', upper):
            return False
    return True


# ==================== Virtual Filesystem ====================

VFS = {
    "/var/log/app.log": """2024-01-15 10:00:01 INFO  Server started on port 8080
2024-01-15 10:00:05 DEBUG Loading configuration from /etc/app/config.yaml
2024-01-15 10:00:10 INFO  Connected to database mysql://db.internal:3306/app
2024-01-15 10:01:22 ERROR Connection timeout to redis://cache.internal:6379
2024-01-15 10:01:23 WARN  Retrying redis connection (attempt 1/3)
2024-01-15 10:01:24 INFO  Redis connection established
2024-01-15 10:02:15 INFO  GET /api/users 200 45ms
2024-01-15 10:02:18 INFO  POST /api/login 200 120ms
2024-01-15 10:02:20 ERROR Authentication failed for user 'test@test.com' — invalid password
2024-01-15 10:02:21 WARN  Rate limit approaching for IP 192.168.1.100
2024-01-15 10:02:30 INFO  GET /api/products 200 32ms
2024-01-15 10:03:00 ERROR Database query timeout after 30s: SELECT * FROM orders WHERE status='pending'
2024-01-15 10:03:01 WARN  Circuit breaker opened for orders-service
2024-01-15 10:03:15 INFO  GET /api/dashboard 500 30100ms
2024-01-15 10:03:20 ERROR NullPointerException in DashboardController.render()
2024-01-15 10:03:21 ERROR Stack trace: at com.app.controller.DashboardController.render(DashboardController.java:42)
2024-01-15 10:04:00 INFO  Health check passed
2024-01-15 10:05:00 INFO  GET /api/users 200 12ms
2024-01-15 10:05:30 INFO  GET /api/products 200 15ms
2024-01-15 10:06:00 INFO  Scheduled task 'cleanup' completed in 200ms""",

    "/var/log/nginx/access.log": """192.168.1.1 - - [15/Jan/2024:10:00:01 +0800] "GET /api/users HTTP/1.1" 200 1234
192.168.1.2 - - [15/Jan/2024:10:00:02 +0800] "POST /api/login HTTP/1.1" 200 567
192.168.1.3 - - [15/Jan/2024:10:00:03 +0800] "GET /api/products HTTP/1.1" 200 4321
10.0.0.5 - - [15/Jan/2024:10:00:04 +0800] "GET /admin HTTP/1.1" 403 89
192.168.1.1 - - [15/Jan/2024:10:00:05 +0800] "GET /api/dashboard HTTP/1.1" 500 234
192.168.1.4 - - [15/Jan/2024:10:00:06 +0800] "POST /api/orders HTTP/1.1" 201 890
192.168.1.2 - - [15/Jan/2024:10:00:07 +0800] "GET /api/users/123 HTTP/1.1" 404 45
10.0.0.5 - - [15/Jan/2024:10:00:08 +0800] "DELETE /api/users/999 HTTP/1.1" 401 67
192.168.1.1 - - [15/Jan/2024:10:00:09 +0800] "GET /api/products?page=2 HTTP/1.1" 200 2345
192.168.1.3 - - [15/Jan/2024:10:00:10 +0800] "GET /api/search?q=test HTTP/1.1" 200 678""",

    "/etc/hosts": """127.0.0.1 localhost
192.168.1.10 app.internal
192.168.1.20 db.internal
192.168.1.30 cache.internal
10.0.0.1 gateway.internal""",
}


def resolve_path(path: str) -> str:
    path = path.strip()
    if path in VFS:
        return path
    for key in VFS:
        if key.endswith(path) or path.endswith(key):
            return key
    return path


# ==================== Command Simulators ====================

def sim_grep(pattern: str, content: str, flags: str = "") -> str:
    lines = content.split('\n')
    ignore_case = 'i' in flags
    invert = 'v' in flags
    count_only = 'c' in flags
    result = []
    for line in lines:
        match = False
        if ignore_case:
            match = pattern.lower() in line.lower()
        else:
            try:
                match = bool(re.search(pattern, line))
            except re.error:
                match = pattern in line
        if invert:
            match = not match
        if match:
            result.append(line)
    if count_only:
        return str(len(result))
    return '\n'.join(result)


def sim_awk(script: str, content: str) -> str:
    lines = content.split('\n')
    m = re.search(r'\{print\s+(.+)\}', script)
    if not m:
        return content
    fields_str = m.group(1)
    field_nums = []
    for part in fields_str.split(','):
        part = part.strip()
        if part.startswith('$'):
            try:
                field_nums.append(int(part[1:]) - 1)
            except ValueError:
                pass
        elif part.startswith('"'):
            field_nums.append(part.strip('"'))
    if not field_nums:
        return content
    result = []
    for line in lines:
        parts = line.split()
        out_parts = []
        for fn in field_nums:
            if isinstance(fn, int):
                if fn < len(parts):
                    out_parts.append(parts[fn])
            else:
                out_parts.append(fn)
        result.append(' '.join(out_parts))
    return '\n'.join(result)


def sim_sort(content: str, flags: str = "") -> str:
    lines = content.strip().split('\n')
    reverse = 'r' in flags
    numeric = 'n' in flags
    if numeric:
        lines.sort(key=lambda x: float(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 0, reverse=reverse)
    else:
        lines.sort(reverse=reverse)
    return '\n'.join(lines)


def sim_uniq(content: str, flags: str = "") -> str:
    lines = content.strip().split('\n')
    count = 'c' in flags
    if count:
        counts = Counter(lines)
        return '\n'.join(f"{c} {line}" for line, c in counts.items())
    seen = set()
    result = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            result.append(line)
    return '\n'.join(result)


def simulate_k6_run(script_code: str, vus: int, duration_sec: int):
    """
    Simulate a k6 load test run with realistic log-normal latency distribution.
    Returns latency percentiles, throughput stats, and per-second data.
    """
    import re
    import hashlib

    # Parse script for endpoint hints
    endpoint = "/api/default"
    method = "GET"
    for line in script_code.split('\n'):
        m = re.search(r"http\.(get|post|put|delete)\s*\(\s*['\"]([^'\"]+)", line, re.IGNORECASE)
        if m:
            method = m.group(1).upper()
            endpoint = m.group(2)
            break

    seed_bytes = hashlib.md5((script_code + str(vus) + str(duration_sec)).encode()).digest()
    rng = random.Random(int.from_bytes(seed_bytes[:4], 'big'))
    base_latency = rng.uniform(20, 80)

    total_requests = int(vus * duration_sec * (1000 / base_latency) * rng.uniform(0.6, 0.95))
    failed_requests = int(total_requests * rng.uniform(0, 0.05))

    # Generate latency samples with log-normal distribution
    latencies = []
    sample_count = min(total_requests, 2000)
    for _ in range(sample_count):
        lat = rng.lognormvariate(math.log(base_latency), 0.4)
        latencies.append(round(lat, 2))
    latencies.sort()

    def percentile(p):
        idx = int(len(latencies) * p / 100)
        return latencies[min(idx, len(latencies) - 1)] if latencies else base_latency

    # Per-second throughput with ramp-up
    per_second = []
    ramp_up = min(30, duration_sec // 3)
    steady_rps = vus * (1000 / base_latency)
    for sec in range(duration_sec):
        factor = (sec + 1) / ramp_up if sec < ramp_up else rng.uniform(0.85, 1.15)
        rps = round(steady_rps * factor, 1)
        errs = round(rps * (failed_requests / max(total_requests, 1)), 1)
        per_second.append({
            "second": sec, "rps": rps, "errors": errs,
            "p95": round(percentile(95) * rng.uniform(0.8, 1.2), 1)
        })

    return {
        "ok": True,
        "endpoint": endpoint, "method": method,
        "vus": vus, "duration_sec": duration_sec,
        "total_requests": total_requests,
        "failed_requests": failed_requests,
        "error_rate": round(failed_requests / max(total_requests, 1) * 100, 2),
        "latency": {
            "min": round(latencies[0], 2) if latencies else base_latency * 0.5,
            "avg": round(sum(latencies) / len(latencies), 2) if latencies else base_latency,
            "p50": round(percentile(50), 2),
            "p90": round(percentile(90), 2),
            "p95": round(percentile(95), 2),
            "p99": round(percentile(99), 2),
            "max": round(latencies[-1], 2) if latencies else base_latency * 3,
        },
        "throughput": {
            "avg_rps": round(steady_rps, 1),
            "peak_rps": round(max(s["rps"] for s in per_second), 1),
        },
        "per_second": per_second,
        "checks_passed": rng.randint(1, 3),
        "checks_total": 3,
    }
