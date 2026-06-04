"""Alembic environment config for QA通关."""

import os
import logging

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context

# Alembic Config object
config = context.config

# Set up logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import ALL models for autogenerate support
from app.database import Base
from app.models.user import User          # noqa: F401
from app.models.tool import Tool          # noqa: F401
from app.models.level import Level, UserLevelProgress  # noqa: F401
from app.models.achievement import Achievement, UserAchievement  # noqa: F401
from app.models.team import Team, TeamMember  # noqa: F401
from app.models.test_case import TestCase  # noqa: F401
from app.models.test_run import TestRun    # noqa: F401

target_metadata = Base.metadata


def get_url():
    """Resolve database URL for migrations (sync driver)."""
    db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./qa_tools.db")
    return db_url.replace("+aiosqlite", "").replace("+asyncpg", "")


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(get_url(), poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
