from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    profession: Mapped[str] = mapped_column(String(160))
    audience: Mapped[str] = mapped_column(Text)
    tone: Mapped[str] = mapped_column(String(200))
    style: Mapped[str] = mapped_column(String(200), default="")
    emoji_preference: Mapped[str] = mapped_column(String(20), default="none")
    cta: Mapped[str] = mapped_column(String(300), default="")
    hashtags: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )
