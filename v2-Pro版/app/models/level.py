from sqlalchemy import String, Integer, Text, JSON, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from app.database import Base


class Level(Base):
    __tablename__ = "levels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order: Mapped[int] = mapped_column(Integer, unique=True)
    stage: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    theory: Mapped[str] = mapped_column(Text)
    demo: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_type: Mapped[str] = mapped_column(String(20))
    task_config: Mapped[dict] = mapped_column(JSON)
    points: Mapped[int] = mapped_column(Integer, default=10)
    tool_id: Mapped[int | None] = mapped_column(ForeignKey("tools.id"), nullable=True)
    required_level_id: Mapped[int | None] = mapped_column(ForeignKey("levels.id"), nullable=True)


class UserLevelProgress(Base):
    __tablename__ = "user_level_progress"
    __table_args__ = (UniqueConstraint("user_id", "level_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    level_id: Mapped[int] = mapped_column(ForeignKey("levels.id"))
    status: Mapped[str] = mapped_column(String(20), default="locked")
    answer: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
