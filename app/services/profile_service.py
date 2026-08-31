from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import UserProfile, utc_now
from app.schemas.profile import EMPTY_PROFILE, ProfileInput

SINGLETON_PROFILE_ID = 1


def get_profile(db: Session) -> UserProfile | None:
    profile = db.get(UserProfile, SINGLETON_PROFILE_ID)
    if profile is not None:
        return profile
    return db.scalars(select(UserProfile).limit(1)).first()


def to_form_values(profile: UserProfile | None) -> dict[str, str]:
    if profile is None:
        return dict(EMPTY_PROFILE)
    return {
        "name": profile.name,
        "profession": profile.profession,
        "audience": profile.audience,
        "tone": profile.tone,
        "style": profile.style,
        "emoji_preference": profile.emoji_preference,
        "cta": profile.cta,
        "hashtags": profile.hashtags,
    }


def upsert_profile(db: Session, payload: ProfileInput) -> UserProfile:
    profile = get_profile(db)
    values = payload.model_dump()
    if profile is None:
        profile = UserProfile(id=SINGLETON_PROFILE_ID, **values)
        db.add(profile)
    else:
        for field, value in values.items():
            setattr(profile, field, value)
        profile.updated_at = utc_now()
    db.commit()
    db.refresh(profile)
    return profile
