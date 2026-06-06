import os
import tempfile
import atexit
import pytest

# Use a temp file for test isolation (in-memory SQLite doesn't share between sync/async engines)
_test_db_fd, _test_db_path = tempfile.mkstemp(suffix=".db", prefix="qa_test_")
os.close(_test_db_fd)
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_test_db_path}"
os.environ["SEED_ADMIN_PASSWORD"] = "qa123456"  # Fixed password for test fixtures


def _cleanup():
    try:
        os.unlink(_test_db_path)
    except (FileNotFoundError, PermissionError):
        pass


atexit.register(_cleanup)


@pytest.fixture(autouse=True)
def _reset_test_state():
    from app.routers.auth import reset_rate_limits, reset_token_blacklist
    reset_rate_limits()
    reset_token_blacklist()
