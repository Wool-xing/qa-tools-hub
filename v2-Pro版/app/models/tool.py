from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Tool(Base):
    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    icon: Mapped[str] = mapped_column(String(10))
    category: Mapped[str] = mapped_column(String(50))
    stage: Mapped[str] = mapped_column(String(100))
    level: Mapped[str] = mapped_column(String(10), default="中级")
    desc: Mapped[str] = mapped_column(Text)
    license: Mapped[str] = mapped_column(String(30))
    url: Mapped[str] = mapped_column(String(300))
    has_tutorial: Mapped[bool] = mapped_column(Boolean, default=False)
