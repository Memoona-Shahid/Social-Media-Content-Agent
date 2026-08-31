from textwrap import dedent
from typing import Literal

TemplateKey = Literal[
    "standard",
    "linkedin_post",
    "x_thread",
    "project_showcase",
    "educational",
    "personal_story",
]

TEMPLATE_OPTIONS: dict[str, dict[str, str]] = {
    "standard": {
        "label": "Standard Post",
        "hint": "Native single post",
        "instructions": dedent(
            """\
            - Write one complete post in the platform's native shape.
            - Follow the platform notes above for length and layout.
            - Do not add extra sections, numbering, or a thread unless the platform requires it."""
        ).strip(),
    },
    "linkedin_post": {
        "label": "LinkedIn Post",
        "hint": "Hook, insight, takeaway",
        "instructions": dedent(
            """\
            - Use a LinkedIn-post shape even if another network is selected: hook, tight body, takeaway.
            - First line must earn the click. No “I’m excited to share.”
            - 2–4 short paragraphs, then one clear insight.
            - Close with a takeaway or a genuine question, not engagement bait.
            - Respect the selected platform’s length limits."""
        ).strip(),
    },
    "x_thread": {
        "label": "X Thread",
        "hint": "Numbered sequence",
        "instructions": dedent(
            """\
            - Write a numbered thread (1/, 2/, 3/), typically 5–8 posts.
            - Post 1 is the hook. Each later post should still make sense on its own.
            - If the platform is X, each post must fit in 280 characters.
            - If another platform is selected, keep the numbered sequence but use that network’s length.
            - This format overrides any instruction to write only a single post.
            - End on a conclusion, not “thread 🧵” or “follow for more.”"""
        ).strip(),
    },
    "project_showcase": {
        "label": "Project Showcase",
        "hint": "Problem, build, result",
        "instructions": dedent(
            """\
            - Structure: the problem, what you made or shipped, one concrete detail of how it works, the result or lesson.
            - Be specific about the work. Do not invent metrics, users, or logos.
            - Keep the tone like a builder explaining the work, not a press release.
            - Fit the selected platform’s length and layout."""
        ).strip(),
    },
    "educational": {
        "label": "Educational Post",
        "hint": "Teach one idea",
        "instructions": dedent(
            """\
            - Teach one idea only.
            - Open with the question, mistake, or confusion your audience actually has.
            - Explain it in plain language, then give one practical takeaway they can use today.
            - Do not stack tips. Do not lecture.
            - Fit the selected platform’s length and layout."""
        ).strip(),
    },
    "personal_story": {
        "label": "Personal Story",
        "hint": "One specific moment",
        "instructions": dedent(
            """\
            - Tell one specific moment, not a career summary.
            - Scene, what was at stake, what changed.
            - Keep reflection short and earned by the story.
            - Do not invent biographical facts.
            - Fit the selected platform’s length and layout."""
        ).strip(),
    },
}


def template_label(template: str) -> str:
    meta = TEMPLATE_OPTIONS.get(template)
    return meta["label"] if meta else template or "Standard Post"
