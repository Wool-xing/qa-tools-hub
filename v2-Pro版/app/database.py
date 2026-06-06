from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import DATABASE_URL

# Sync: strip async driver prefix
_sync_url = DATABASE_URL.replace("+aiosqlite", "").replace("+asyncpg", "")
sync_engine = create_engine(_sync_url, echo=False)
SyncSession = sessionmaker(sync_engine)

# Async: ensure async driver prefix
_async_url = DATABASE_URL
if "+aiosqlite" not in _async_url and "+asyncpg" not in _async_url:
    if "sqlite" in _async_url:
        _async_url = _async_url.replace("sqlite://", "sqlite+aiosqlite://")
    elif "postgresql" in _async_url:
        _async_url = _async_url.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(_async_url, echo=False, pool_size=5, max_overflow=5)
async_session = async_sessionmaker(engine, expire_on_commit=False)


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
