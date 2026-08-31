from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.templates import TemplateKey

Platform = Literal["linkedin", "x", "instagram", "threads"]

PLATFORM_OPTIONS: dict[str, dict[str, str]] = {
    "linkedin": {
        "label": "LinkedIn",
        "hint": "Professional feed",
    },
    "x": {
        "label": "X",
        "hint": "Short public post",
    },
    "instagram": {
        "label": "Instagram",
        "hint": "Caption-first",
    },
    "threads": {
        "label": "Threads",
        "hint": "Conversational feed",
    },
}

EMPTY_BRIEF: dict[str, str] = {
    "topic": "",
    "platform": "",
    "template": "standard",
}


class TopicBrief(BaseModel):
    topic: str = Field(max_length=500)
    platform: Platform
    template: TemplateKey = "standard"

    @field_validator("topic", mode="before")
    @classmethod
    def strip_topic(cls, value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @field_validator("topic")
    @classmethod
    def topic_required(cls, value: str) -> str:
        if not value:
            raise ValueError("Enter a topic.")
        return value

    @field_validator("platform", mode="before")
    @classmethod
    def platform_required(cls, value: Any) -> str:
        if value is None or str(value).strip() == "":
            raise ValueError("Choose a platform.")
        return str(value).strip().lower()

    @field_validator("template", mode="before")
    @classmethod
    def template_default(cls, value: Any) -> str:
        if value is None or str(value).strip() == "":
            return "standard"
        return str(value).strip().lower()
