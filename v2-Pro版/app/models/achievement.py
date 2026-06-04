"""Achievement models for QA通关."""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Achievement(Base):
    __tablename__ = "achievements"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    icon: Mapped[str] = mapped_column(String(10))
    name: Mapped[str] = mapped_column(String(100))
    desc: Mapped[str] = mapped_column(String(200))
    condition_type: Mapped[str] = mapped_column(String(30))  # completed_count, stage_done, lab_count
    condition_value: Mapped[str] = mapped_column(String(50))  # "5", "beginner", "3"


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    achievement_key: Mapped[str] = mapped_column(String(50))
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
