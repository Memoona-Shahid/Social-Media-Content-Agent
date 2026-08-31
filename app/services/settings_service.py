from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.models.profile import utc_now
from app.models.settings import AppSettings
from app.schemas.settings import LLM_OPTIONS, THEME_OPTIONS, SettingsInput
from app.schemas.topic import PLATFORM_OPTIONS

SINGLETON_SETTINGS_ID = 1


@dataclass(frozen=True, slots=True)
class AppPreferences:
    default_platform: str
    llm_provider: str
    theme: str

    def to_form_values(self) -> dict[str, str]:
        return {
            "default_platform": self.default_platform,
            "llm_provider": self.llm_provider,
            "theme": self.theme,
        }

    def to_dict(self) -> dict[str, object]:
        return {
            "default_platform": self.default_platform,
            "default_platform_label": platform_choice_label(self.default_platform),
            "llm_provider": self.llm_provider,
            "llm_provider_label": llm_choice_label(self.llm_provider),
            "theme": self.theme,
            "theme_label": theme_choice_label(self.theme),
        }


def platform_choice_label(platform: str) -> str:
    meta = PLATFORM_OPTIONS.get(platform)
    return meta["label"] if meta else platform


def llm_choice_label(provider: str) -> str:
    meta = LLM_OPTIONS.get(provider)
    return meta["label"] if meta else provider


def theme_choice_label(theme: str) -> str:
    meta = THEME_OPTIONS.get(theme)
    return meta["label"] if meta else theme


def default_preferences(settings: Settings | None = None) -> AppPreferences:
    config = settings or get_settings()
    return AppPreferences(
        default_platform="linkedin",
        llm_provider=config.active_provider,
        theme="light",
    )


def get_preferences(db: Session, settings: Settings | None = None) -> AppPreferences:
    try:
        row = db.get(AppSettings, SINGLETON_SETTINGS_ID)
        if row is None:
            row = db.scalars(select(AppSettings).limit(1)).first()
    except (OperationalError, ProgrammingError):
        return default_preferences(settings)
    if row is None:
        return default_preferences(settings)

    platform = row.default_platform if row.default_platform in PLATFORM_OPTIONS else "linkedin"
    provider = row.llm_provider if row.llm_provider in LLM_OPTIONS else default_preferences(settings).llm_provider
    theme = row.theme if row.theme in THEME_OPTIONS else "light"
    return AppPreferences(
        default_platform=platform,
        llm_provider=provider,
        theme=theme,
    )


def load_preferences() -> AppPreferences:
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        return get_preferences(db)
    except (OperationalError, ProgrammingError):
        return default_preferences()
    finally:
        db.close()


def upsert_preferences(db: Session, payload: SettingsInput) -> AppPreferences:
    values = payload.model_dump()
    row = db.get(AppSettings, SINGLETON_SETTINGS_ID)
    if row is None:
        row = db.scalars(select(AppSettings).limit(1)).first()
    if row is None:
        row = AppSettings(id=SINGLETON_SETTINGS_ID, **values)
        db.add(row)
    else:
        row.default_platform = values["default_platform"]
        row.llm_provider = values["llm_provider"]
        row.theme = values["theme"]
        row.updated_at = utc_now()
    db.commit()
    db.refresh(row)
    return get_preferences(db)


def resolve_llm(
    prefs: AppPreferences,
    settings: Settings | None = None,
) -> tuple[str, bool, str]:
    config = settings or get_settings()
    provider = prefs.llm_provider if prefs.llm_provider in LLM_OPTIONS else config.active_provider
    if provider == "openai":
        return provider, config.openai_configured, "Add OPENAI_API_KEY to .env to generate posts."
    return provider, config.groq_configured, "Add GROQ_API_KEY to .env to generate posts."
