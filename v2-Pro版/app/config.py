import os
import logging

logger = logging.getLogger("qa-tools")

# ==================== Database ====================

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./qa_tools.db")

# ==================== Security ====================

_WEAK_SECRETS = {"dev-secret-change-me-in-production!!", "change-me-in-production"}
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me-in-production!!")
if SECRET_KEY in _WEAK_SECRETS:
    logger.warning("SECURITY: Using default SECRET_KEY. Set SECRET_KEY env var for production.")

def _safe_int_env(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        logger.warning("Invalid int for env %s, using default %d", key, default)
        return default


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = _safe_int_env("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24)

# ==================== CORS ====================

_CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:8005,http://localhost:8090")
CORS_ORIGINS = [o.strip() for o in _CORS_ORIGINS.split(",") if o.strip()]

# ==================== Email (SMTP) ====================

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = _safe_int_env("SMTP_PORT", 587)
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@qatools.local")

# ==================== Security Headers ====================

HSTS_MAX_AGE = _safe_int_env("HSTS_MAX_AGE", 31536000)
CSP_POLICY = os.getenv("CSP_POLICY", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'")


def check_config():
    """Validate config at startup. Returns list of warnings."""
    issues = []
    if SECRET_KEY in _WEAK_SECRETS:
        issues.append("SECRET_KEY is default — change in production")
    if ACCESS_TOKEN_EXPIRE_MINUTES > 60 * 24 * 7:
        issues.append("ACCESS_TOKEN_EXPIRE_MINUTES is very long (>7 days)")
    if not SMTP_HOST:
        issues.append("SMTP_HOST not set — password reset emails disabled")
    return issues
