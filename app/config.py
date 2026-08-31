from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Social Media Content Agent"
    app_env: str = "development"
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8000
    secret_key: str = "change-me-in-production"
    database_url: str = "sqlite:///./data/app.db"
    groq_api_key: str = ""
    openai_api_key: str = ""
    llm_provider: str = "groq"
    groq_model: str = "llama-3.3-70b-versatile"
    openai_model: str = "gpt-4o-mini"
    llm_timeout_seconds: float = 45
    llm_temperature: float = 0.7

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def groq_configured(self) -> bool:
        return bool(self.groq_api_key.strip())

    @property
    def openai_configured(self) -> bool:
        return bool(self.openai_api_key.strip())

    @property
    def active_provider(self) -> str:
        provider = self.llm_provider.strip().lower()
        return provider if provider in {"groq", "openai"} else "groq"

    @property
    def llm_ready(self) -> bool:
        if self.active_provider == "openai":
            return self.openai_configured
        return self.groq_configured

    @property
    def llm_setup_message(self) -> str:
        if self.active_provider == "openai":
            return "Add OPENAI_API_KEY to .env to generate posts."
        return "Add GROQ_API_KEY to .env to generate posts."


@lru_cache
def get_settings() -> Settings:
    return Settings()
