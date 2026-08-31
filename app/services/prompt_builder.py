from dataclasses import dataclass
from textwrap import dedent

from app.schemas.templates import TEMPLATE_OPTIONS, template_label
from app.schemas.topic import PLATFORM_OPTIONS, TopicBrief
from app.services.memory_service import BrandMemory
from app.services.topic_service import platform_label

EMOJI_GUIDANCE = {
    "none": "Do not use emoji.",
    "light": "Use at most one or two emoji, and only if they add clarity.",
    "frequent": "Use emoji naturally to support rhythm, without cluttering the copy.",
}

PLATFORM_CONSTRAINTS = {
    "linkedin": dedent(
        """\
        - Write a professional feed post, not an article.
        - Open with a specific hook in the first line.
        - Use short paragraphs and plenty of line breaks.
        - Aim for roughly 150–250 words.
        - Use at most three relevant hashtags, placed at the end.
        - Avoid slang, clickbait, and engagement-bait questions."""
    ),
    "x": dedent(
        """\
        - Write a single post that fits in 280 characters.
        - Be sharp and specific; cut filler.
        - Use at most two hashtags, and only if they earn the space.
        - Do not write a thread unless the topic cannot fit in one post.
        - Avoid hashtag stuffing and “thread 🧵” openers."""
    ),
    "instagram": dedent(
        """\
        - Write a caption, not a feed essay.
        - Put the hook in the first line, before the fold.
        - Use short lines and clear breaks so it reads on a phone.
        - Place hashtags after the caption, not in the first line.
        - Keep the voice personal; avoid sounding like an ad."""
    ),
    "threads": dedent(
        """\
        - Write a conversational feed post, closer to a remark than an article.
        - Keep it shorter than a LinkedIn post.
        - Sound like a person talking, not a brand announcement.
        - Use at most two hashtags, optional.
        - Do not use a hard sales close."""
    ),
}


@dataclass(frozen=True, slots=True)
class BuiltPrompt:
    ready: bool
    topic: str = ""
    platform: str = ""
    platform_label: str = ""
    template: str = ""
    template_label: str = ""
    system: str = ""
    user: str = ""
    missing: tuple[str, ...] = ()

    def as_messages(self) -> list[dict[str, str]]:
        if not self.ready:
            return []
        return [
            {"role": "system", "content": self.system},
            {"role": "user", "content": self.user},
        ]

    def to_dict(self) -> dict[str, object]:
        return {
            "ready": self.ready,
            "topic": self.topic,
            "platform": self.platform,
            "platform_label": self.platform_label,
            "template": self.template,
            "template_label": self.template_label,
            "system": self.system,
            "user": self.user,
            "messages": self.as_messages(),
            "missing": list(self.missing),
        }


def build_prompt(memory: BrandMemory, brief: TopicBrief | None) -> BuiltPrompt:
    missing: list[str] = []
    if brief is None:
        missing.append("brief")
    if not memory.loaded:
        missing.append("memory")
    if missing:
        return BuiltPrompt(ready=False, missing=tuple(missing))

    assert brief is not None
    label = platform_label(brief.platform)
    format_label = template_label(brief.template)
    system = _system_prompt(memory, brief, label, format_label)
    user = _user_prompt(brief, label, format_label)
    return BuiltPrompt(
        ready=True,
        topic=brief.topic,
        platform=brief.platform,
        platform_label=label,
        template=brief.template,
        template_label=format_label,
        system=system,
        user=user,
    )


def _system_prompt(
    memory: BrandMemory,
    brief: TopicBrief,
    label: str,
    format_label: str,
) -> str:
    platform_meta = PLATFORM_OPTIONS[brief.platform]
    constraints = PLATFORM_CONSTRAINTS[brief.platform]
    template_meta = TEMPLATE_OPTIONS.get(brief.template, TEMPLATE_OPTIONS["standard"])
    emoji_rule = EMOJI_GUIDANCE.get(memory.emoji_preference, EMOJI_GUIDANCE["none"])
    style = memory.style or "Clear, concrete, and easy to scan."
    cta = memory.cta or "No default call to action. End naturally if a CTA does not fit."
    hashtags = memory.hashtags or "No default hashtags."

    return dedent(
        f"""\
        You are a social media ghostwriter for {memory.name}, a {memory.profession}.
        Write in their voice. Do not mention that you are an AI.

        BRAND VOICE
        - Audience: {memory.audience}
        - Tone: {memory.tone}
        - Style: {style}
        - Emoji: {emoji_rule}
        - Call to action: {cta}
        - Hashtags: {hashtags}

        PLATFORM
        - Network: {label} ({platform_meta["hint"]})
        {constraints}

        FORMAT
        - Template: {format_label}
        {template_meta["instructions"]}
        - If FORMAT conflicts with PLATFORM notes, follow FORMAT and still respect hard length limits.

        RULES
        - Stay on the given topic. Do not add unrelated ideas.
        - Do not invent facts, metrics, customers, or product claims.
        - Return only the post copy. No title, preamble, or explanation.
        - Sound like this person, not a generic brand or a template."""
    ).strip()


def _user_prompt(brief: TopicBrief, label: str, format_label: str) -> str:
    return dedent(
        f"""\
        Write this as a {format_label} for {label}.

        Topic:
        {brief.topic}"""
    ).strip()
