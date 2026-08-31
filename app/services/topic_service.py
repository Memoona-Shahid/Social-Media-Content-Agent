from fastapi import Request
from pydantic import ValidationError

from app.schemas.topic import EMPTY_BRIEF, PLATFORM_OPTIONS, TopicBrief

SESSION_KEY = "topic_brief"


def platform_label(platform: str) -> str:
    meta = PLATFORM_OPTIONS.get(platform)
    return meta["label"] if meta else platform


def get_brief(request: Request) -> TopicBrief | None:
    raw = request.session.get(SESSION_KEY)
    if not raw:
        return None
    try:
        return TopicBrief.model_validate(raw)
    except ValidationError:
        return None


def save_brief(request: Request, brief: TopicBrief) -> None:
    request.session[SESSION_KEY] = brief.model_dump()


def brief_form_values(brief: TopicBrief | None) -> dict[str, str]:
    if brief is None:
        return dict(EMPTY_BRIEF)
    return brief.model_dump()


def brief_payload(brief: TopicBrief | None) -> dict[str, object]:
    if brief is None:
        return {
            "captured": False,
            "topic": "",
            "platform": "",
            "platform_label": "",
        }
    return {
        "captured": True,
        "topic": brief.topic,
        "platform": brief.platform,
        "platform_label": platform_label(brief.platform),
    }
