from typing import Any, Literal

from pydantic import BaseModel, field_validator

from app.schemas.topic import Platform

LlmProvider = Literal["groq", "openai"]
Theme = Literal["light", "dark"]

LLM_OPTIONS: dict[str, dict[str, str]] = {
    "groq": {
        "label": "Groq",
        "hint": "Fast open models",
    },
    "openai": {
        "label": "OpenAI",
        "hint": "GPT models",
    },
}

THEME_OPTIONS: dict[str, dict[str, str]] = {
    "light": {
        "label": "Light",
        "hint": "Paper studio",
    },
    "dark": {
        "label": "Dark",
        "hint": "Low-light desk",
    },
}


class SettingsInput(BaseModel):
    default_platform: Platform
    llm_provider: LlmProvider
    theme: Theme

    @field_validator("default_platform", "llm_provider", "theme", mode="before")
    @classmethod
    def normalize_choice(cls, value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip().lower()
