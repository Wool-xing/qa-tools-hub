from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(300))
    steps: Mapped[str] = mapped_column(Text)
    expected_result: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(10), default="P2")  # P0-P4
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft/ready/running/passed/failed
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True, index=True)
    level_id: Mapped[int | None] = mapped_column(ForeignKey("levels.id"), nullable=True, index=True)
    tags: Mapped[str | None] = mapped_column(String(500), nullable=True)  # comma-separated
    folder: Mapped[str] = mapped_column(String(100), default="默认", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), index=True)
