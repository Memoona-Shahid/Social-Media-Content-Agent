from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

EmojiPreference = Literal["none", "light", "frequent"]

EMPTY_PROFILE: dict[str, str] = {
    "name": "",
    "profession": "",
    "audience": "",
    "tone": "",
    "style": "",
    "emoji_preference": "none",
    "cta": "",
    "hashtags": "",
}


class ProfileInput(BaseModel):
    name: str = Field(max_length=120)
    profession: str = Field(max_length=160)
    audience: str = Field(max_length=500)
    tone: str = Field(max_length=200)
    style: str = Field(default="", max_length=200)
    emoji_preference: EmojiPreference = "none"
    cta: str = Field(default="", max_length=300)
    hashtags: str = Field(default="", max_length=500)

    @field_validator(
        "name",
        "profession",
        "audience",
        "tone",
        "style",
        "cta",
        "hashtags",
        mode="before",
    )
    @classmethod
    def strip_text(cls, value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @field_validator("name")
    @classmethod
    def name_required(cls, value: str) -> str:
        if not value:
            raise ValueError("Enter your name.")
        return value

    @field_validator("profession")
    @classmethod
    def profession_required(cls, value: str) -> str:
        if not value:
            raise ValueError("Enter your profession.")
        return value

    @field_validator("audience")
    @classmethod
    def audience_required(cls, value: str) -> str:
        if not value:
            raise ValueError("Describe your audience.")
        return value

    @field_validator("tone")
    @classmethod
    def tone_required(cls, value: str) -> str:
        if not value:
            raise ValueError("Describe your tone.")
        return value

    @field_validator("hashtags")
    @classmethod
    def normalize_hashtags(cls, value: str) -> str:
        tokens = [part.strip() for part in value.replace(",", " ").split() if part.strip()]
        unique: list[str] = []
        seen: set[str] = set()
        for token in tokens:
            tag = token if token.startswith("#") else f"#{token}"
            tag = tag.replace(" ", "")
            key = tag.lower()
            if tag == "#" or key in seen:
                continue
            seen.add(key)
            unique.append(tag)
        return " ".join(unique)
