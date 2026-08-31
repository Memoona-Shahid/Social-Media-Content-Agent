from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.profile import utc_now
from app.schemas.templates import template_label
from app.schemas.topic import PLATFORM_OPTIONS


class GeneratedPost(Base):
    __tablename__ = "generated_posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic: Mapped[str] = mapped_column(String(500))
    platform: Mapped[str] = mapped_column(String(32))
    content: Mapped[str] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(String(32))
    model: Mapped[str] = mapped_column(String(120))
    voice_name: Mapped[str] = mapped_column(String(120), default="")
    template: Mapped[str] = mapped_column(String(64), default="standard")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )

    @property
    def platform_label(self) -> str:
        meta = PLATFORM_OPTIONS.get(self.platform)
        return meta["label"] if meta else self.platform

    @property
    def template_label(self) -> str:
        return template_label(self.template or "standard")

    @property
    def excerpt(self) -> str:
        text = " ".join(self.content.split())
        if len(text) <= 160:
            return text
        return text[:157].rstrip() + "..."

    @property
    def created_label(self) -> str:
        value = self.created_at
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.strftime("%d %b %Y, %H:%M UTC")

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "topic": self.topic,
            "platform": self.platform,
            "platform_label": self.platform_label,
            "content": self.content,
            "provider": self.provider,
            "model": self.model,
            "voice_name": self.voice_name,
            "template": self.template or "standard",
            "template_label": self.template_label,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_label": self.created_label,
            "excerpt": self.excerpt,
        }
