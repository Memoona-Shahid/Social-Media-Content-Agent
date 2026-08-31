from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.profile import UserProfile
from app.services.profile_service import get_profile


class MemoryNotLoadedError(RuntimeError):
    """Raised when a generation path needs a saved brand voice and none exists."""


@dataclass(frozen=True, slots=True)
class BrandMemory:
    loaded: bool
    name: str = ""
    profession: str = ""
    audience: str = ""
    tone: str = ""
    style: str = ""
    emoji_preference: str = "none"
    cta: str = ""
    hashtags: str = ""
    updated_at: datetime | None = None

    @classmethod
    def empty(cls) -> "BrandMemory":
        return cls(loaded=False)

    @classmethod
    def from_profile(cls, profile: UserProfile) -> "BrandMemory":
        return cls(
            loaded=True,
            name=profile.name,
            profession=profile.profession,
            audience=profile.audience,
            tone=profile.tone,
            style=profile.style,
            emoji_preference=profile.emoji_preference,
            cta=profile.cta,
            hashtags=profile.hashtags,
            updated_at=profile.updated_at,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "loaded": self.loaded,
            "name": self.name,
            "profession": self.profession,
            "audience": self.audience,
            "tone": self.tone,
            "style": self.style,
            "emoji_preference": self.emoji_preference,
            "cta": self.cta,
            "hashtags": self.hashtags,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


def load_brand_memory(db: Session) -> BrandMemory:
    profile = get_profile(db)
    if profile is None:
        return BrandMemory.empty()
    return BrandMemory.from_profile(profile)


def ensure_loaded(memory: BrandMemory) -> BrandMemory:
    if not memory.loaded:
        raise MemoryNotLoadedError(
            "Brand voice is not saved. Create a profile before generating content."
        )
    return memory
