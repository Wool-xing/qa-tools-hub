import os
import logging
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger("qa-tools")


def _safe_int_env(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        logger.warning("Invalid int for env %s, using default %d", key, default)
        return default


# ==================== Database ====================

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/qa_tools.db")

# ==================== Security ====================

_WEAK_SECRETS = {"dev-secret-change-me-in-production!!", "change-me-in-production"}
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me-in-production!!")
if SECRET_KEY in _WEAK_SECRETS:
    logger.warning("SECURITY: Using default SECRET_KEY. Set SECRET_KEY env var for production.")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = _safe_int_env("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24)
PASSWORD_MIN_LEN = _safe_int_env("PASSWORD_MIN_LEN", 8)

# ==================== Rate Limiting ====================

RATE_LIMIT_WINDOW = _safe_int_env("RATE_LIMIT_WINDOW", 60)
RATE_LIMIT_MAX = _safe_int_env("RATE_LIMIT_MAX", 5)

# ==================== CORS ====================

_CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:8005,http://localhost:8090")
CORS_ORIGINS = [o.strip() for o in _CORS_ORIGINS.split(",") if o.strip()]

# ==================== Email (SMTP) ====================

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = _safe_int_env("SMTP_PORT", 587)
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@qatools.local")
SMTP_TIMEOUT = _safe_int_env("SMTP_TIMEOUT", 10)
# Base URL for generating links in emails (password reset etc.)
# In production set this to your public domain, e.g. https://qa.example.com
BASE_URL = os.getenv("BASE_URL", "")

# ==================== Sandbox ====================

SANDBOX_TIMEOUT = _safe_int_env("SANDBOX_TIMEOUT", 5)

# ==================== Logging ====================

LOG_MAX_BYTES = _safe_int_env("LOG_MAX_BYTES", 10_485_760)  # 10 MB
LOG_BACKUP_COUNT = _safe_int_env("LOG_BACKUP_COUNT", 5)

# ==================== Limits ====================

MAX_XLSX_BYTES = _safe_int_env("MAX_XLSX_BYTES", 5 * 1024 * 1024)  # 5 MB
BULK_UPDATE_LIMIT = _safe_int_env("BULK_UPDATE_LIMIT", 200)
SQL_ROW_LIMIT = _safe_int_env("SQL_ROW_LIMIT", 100)
PERF_VUS_MAX = _safe_int_env("PERF_VUS_MAX", 500)
PERF_DURATION_MAX = _safe_int_env("PERF_DURATION_MAX", 600)
ADMIN_PAGE_LIMIT = _safe_int_env("ADMIN_PAGE_LIMIT", 50)
LEADERBOARD_LIMIT = _safe_int_env("LEADERBOARD_LIMIT", 10)
SKILL_GAP_WEAK_THRESHOLD = _safe_int_env("SKILL_GAP_WEAK_THRESHOLD", 80)
SKILL_GAP_STRONG_THRESHOLD = _safe_int_env("SKILL_GAP_STRONG_THRESHOLD", 90)

# ==================== Seed ====================

SEED_ADMIN_USERNAME = os.getenv("SEED_ADMIN_USERNAME", "qatest")
SEED_ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "qatest@qa.local")
# WARNING: Change this in production! If unset, uses a random password printed at startup.
SEED_ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "")

# ==================== Security Headers ====================

HSTS_MAX_AGE = _safe_int_env("HSTS_MAX_AGE", 31536000)
CSP_POLICY = os.getenv("CSP_POLICY", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'")


def check_config():
    """Validate config at startup. Returns list of warnings."""
    issues = []
    if SECRET_KEY in _WEAK_SECRETS:
        issues.append("SECRET_KEY is default — change in production")
    if ACCESS_TOKEN_EXPIRE_MINUTES > 60 * 24 * 7:
        issues.append("ACCESS_TOKEN_EXPIRE_MINUTES is very long (>7 days)")
    if not SMTP_HOST:
        issues.append("SMTP_HOST not set — password reset emails disabled")
    if SEED_ADMIN_PASSWORD and len(SEED_ADMIN_PASSWORD) < 8:
        issues.append("SEED_ADMIN_PASSWORD is too short (< 8 chars)")
    if not BASE_URL:
        issues.append("BASE_URL not set — password reset links may use wrong host")
    return issues
