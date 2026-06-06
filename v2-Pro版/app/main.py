import os
import uuid
import time
import asyncio
import logging
import re
from logging.handlers import RotatingFileHandler
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.responses import Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from app import __version__
from app.database import init_db, sync_engine
from app.seed import seed
from app.config import CORS_ORIGINS, check_config, HSTS_MAX_AGE, CSP_POLICY, LOG_MAX_BYTES, LOG_BACKUP_COUNT
from app.routers import auth, levels, labs, admin, testcases, analytics, teams
from app.routers.auth import get_current_user

# Logging: stdout + rotating file
LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, handlers=[
    logging.StreamHandler(),
    RotatingFileHandler(os.path.join(LOG_DIR, "app.log"), maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8"),
])
logger = logging.getLogger("qa-tools")


# ==================== Global Exception Handler ====================

async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception("Unhandled error request_id=%s path=%s", request_id, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "request_id": request_id},
    )


# ==================== Security Headers Middleware ====================

async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    # Cache static assets (hashed filenames = immutable)
    if request.url.path.startswith("/assets/"):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["X-Download-Options"] = "noopen"
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = f"max-age={HSTS_MAX_AGE}; includeSubDomains"
    response.headers["Content-Security-Policy"] = CSP_POLICY
    response.headers["X-Request-Id"] = getattr(request.state, "request_id", "")
    return response


# ==================== Prometheus Metrics ====================

_http_requests = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
_http_latency = Histogram("http_request_duration_ms", "HTTP request latency", ["method", "path"])
_http_inflight = Gauge("http_requests_inflight", "Currently in-flight requests")

_METRICS_EXCLUDED_PATHS = {"/metrics", "/health", "/favicon.ico", "/docs", "/openapi.json"}


def _metric_path(path: str) -> str:
    """Bucket paths like /api/levels/5 → /api/levels/{id}"""
    path = re.sub(r'/\d+', '/{id}', path)
    path = re.sub(r'/[a-f0-9-]{8,}', '/{token}', path)
    return path


# ==================== Request ID Middleware ====================

async def request_id_middleware(request: Request, call_next):
    request.state.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    request.state.start_time = time.time()
    if request.url.path not in _METRICS_EXCLUDED_PATHS:
        _http_inflight.inc()
    response = await call_next(request)
    elapsed_ms = int((time.time() - request.state.start_time) * 1000)
    response.headers["X-Request-Id"] = request.state.request_id
    response.headers["X-Response-Time"] = str(elapsed_ms)
    if request.url.path not in _METRICS_EXCLUDED_PATHS:
        _http_inflight.dec()
        mp = _metric_path(request.url.path)
        _http_requests.labels(method=request.method, path=mp, status=str(response.status_code)).inc()
        _http_latency.labels(method=request.method, path=mp).observe(elapsed_ms)
    logger.info("%s %s %s %sms %s", request.state.request_id, request.method, request.url.path, response.status_code, elapsed_ms)
    return response


# ==================== Lifespan ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run migrations before create_all to ensure schema is current
    try:
        from alembic.config import Config
        from alembic import command
        alembic_ini = os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini")
        if os.path.isfile(alembic_ini):
            alembic_cfg = Config(alembic_ini)
            command.upgrade(alembic_cfg, "head")
        else:
            logger.warning("alembic.ini not found — skipping migrations, using create_all fallback")
    except Exception as e:
        logger.warning("Migration failed: %s — falling back to create_all", e)
    init_db()
    seed()
    for issue in check_config():
        logger.warning("Config: %s", issue)
    logger.info("QA通关 API v%s started", __version__)
    yield
    logger.info("QA通关 API v%s shutting down", __version__)


# ==================== App ====================

app = FastAPI(
    title="QA通关",
    version=__version__,
    lifespan=lifespan,
    description="测试工程师一站式学习与工具平台 API — 102关学习系统 + 21实验室 + 成就系统",
    docs_url="/docs",
    redoc_url=None,
)

# Middleware order: last added = outermost
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True, allow_methods=["GET","POST","PUT","DELETE","PATCH"], allow_headers=["Authorization","Content-Type","X-Request-ID"])
app.middleware("http")(security_headers_middleware)
app.middleware("http")(request_id_middleware)

app.add_exception_handler(Exception, global_exception_handler)

app.include_router(auth.router)
app.include_router(levels.router)
app.include_router(labs.router)
app.include_router(admin.router)
app.include_router(testcases.router)
app.include_router(analytics.router)
app.include_router(teams.router)

static_dir = os.path.join(os.path.dirname(__file__), "static")
assets_dir = os.path.join(static_dir, "assets")
if os.path.isdir(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.get("/manifest.json", include_in_schema=False)
async def manifest():
    manifest_path = os.path.join(static_dir, "manifest.json")
    if os.path.isfile(manifest_path):
        return FileResponse(manifest_path, media_type="application/json")
    raise HTTPException(status_code=404)


# ==================== Routes ====================

@app.get("/health")
async def health():
    db_ok = False
    try:
        from sqlalchemy import text
        with sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        logger.warning("Health check DB error: %s", e)
    return {"status": "ok" if db_ok else "degraded", "service": "qa-tools-pro", "version": __version__, "database": "connected" if db_ok else "disconnected"}


@app.get("/metrics", include_in_schema=False)
async def metrics_prometheus(request: Request):
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"message": f"QA通关 API v{__version__}", "docs": "/docs"}


# Mock service virtualisation endpoint — must be before SPA fallback
@app.api_route("/mock/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], include_in_schema=False)
async def mock_handler(request: Request, path: str,
                       user = Depends(get_current_user)):
    from app.routers.labs import mock_store, mock_call_counts
    key = f"{request.method}:{path}"
    config = mock_store.get(key)
    if not config:
        raise HTTPException(status_code=404, detail=f"No mock registered for {key}")

    # Record call
    mock_call_counts.setdefault(key, []).append({"timestamp": time.time(), "path": path, "method": request.method})

    call_count = len(mock_call_counts.get(key, []))

    # Sequence handling
    sequence = config.get("sequence", [])
    if sequence:
        seq_idx = min(call_count - 1, len(sequence) - 1)
        seq_item = sequence[seq_idx]
        status = seq_item.get("status_code", config.get("status_code", 200))
        body = seq_item.get("response_body", config.get("response_body", ""))
        delay = seq_item.get("delay_ms", config.get("delay_ms", 0)) / 1000
    else:
        status = config.get("status_code", 200)
        body = config.get("response_body", "")
        delay = config.get("delay_ms", 0) / 1000

    if delay:
        await asyncio.sleep(delay)

    return Response(content=body, status_code=status, media_type="application/json")


@app.get("/{path:path}")
async def spa_fallback(path: str):
    if path.startswith("api/") or path == "docs" or path == "openapi.json":
        raise HTTPException(status_code=404)
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404)
