import os
from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import DATABASE_URL

# Allow explicit async URL override for non-standard drivers
_async_url = os.getenv("ASYNC_DATABASE_URL", "")
if not _async_url:
    _async_url = DATABASE_URL
    parsed = make_url(_async_url)
    if "aiosqlite" not in parsed.drivername and "asyncpg" not in parsed.drivername:
        if parsed.drivername == "sqlite":
            _async_url = _async_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        elif parsed.drivername == "postgresql":
            _async_url = _async_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Sync: strip async driver prefix
_sync_url = DATABASE_URL
parsed_sync = make_url(_sync_url)
_async_prefixes = ("aiosqlite", "asyncpg", "asyncmy")
for prefix in _async_prefixes:
    if prefix in parsed_sync.drivername:
        _sync_url = _sync_url.replace(f"+{prefix}", "", 1)
        break

# Pool config from env
_pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
_pool_overflow = int(os.getenv("DB_POOL_OVERFLOW", "5"))

sync_engine = create_engine(_sync_url, echo=False)
SyncSession = sessionmaker(sync_engine)

engine = create_async_engine(_async_url, echo=False, pool_size=_pool_size, max_overflow=_pool_overflow)
async_session = async_sessionmaker(engine, expire_on_commit=False)


def _enable_sqlite_fk(dbapi_conn, _record):
    # SQLite ignores FK constraints unless enabled per-connection.
    # Without this, ondelete=CASCADE silently does nothing and deletes
    # leave orphan rows (QA-2026-08-18 HIGH #5).
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


if sync_engine.dialect.name == "sqlite":
    event.listen(sync_engine, "connect", _enable_sqlite_fk)
if engine.dialect.name == "sqlite":
    event.listen(engine.sync_engine, "connect", _enable_sqlite_fk)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


def init_db():
    # Import all models so Base.metadata picks them up
    import app.models.user          # noqa: F401
    import app.models.level         # noqa: F401
    import app.models.test_case     # noqa: F401
    import app.models.test_run      # noqa: F401
    import app.models.team          # noqa: F401
    import app.models.tool          # noqa: F401
    import app.models.achievement   # noqa: F401
    Base.metadata.create_all(sync_engine)
