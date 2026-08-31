from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from pydantic import ValidationError

from app.dependencies import get_brand_memory, get_built_prompt
from app.schemas.topic import EMPTY_BRIEF, PLATFORM_OPTIONS, TopicBrief
from app.services import topic_service
from app.services.generator import get_generation, pop_generation_error
from app.services.memory_service import BrandMemory
from app.services.prompt_builder import BuiltPrompt
from app.templating import build_template_context, templates

router = APIRouter(tags=["topic"])


def _friendly_errors(exc: ValidationError) -> dict[str, str]:
    errors: dict[str, str] = {}
    for item in exc.errors():
        field = str(item.get("loc", ("form",))[0])
        message = item.get("msg", "Invalid value.")
        if message.startswith("Value error, "):
            message = message.removeprefix("Value error, ")
        elif field == "platform":
            message = "Choose LinkedIn, X, Instagram, or Threads."
        elif "should have at most" in message:
            message = "This value is too long."
        errors[field] = message
    return errors


def _render(
    request: Request,
    *,
    memory: BrandMemory,
    prompt: BuiltPrompt,
    values: dict[str, str],
    errors: dict[str, str] | None = None,
    ready: bool = False,
    generated: bool = False,
) -> HTMLResponse:
    brief = topic_service.get_brief(request)
    context = build_template_context(
        request=request,
        page_title="Compose",
        active_nav="compose",
        memory=memory,
        values=values,
        errors=errors or {},
        ready=ready,
        platforms=PLATFORM_OPTIONS,
        captured_brief=brief,
        platform_label=topic_service.platform_label(brief.platform) if brief else "",
        prompt=prompt,
        generation=get_generation(request.session),
        generate_error=pop_generation_error(request.session),
        generated=generated,
    )
    return templates.TemplateResponse(request, "compose.html", context)


@router.get("/compose", response_class=HTMLResponse)
def compose_page(
    request: Request,
    ready: int = 0,
    generated: int = 0,
    memory: BrandMemory = Depends(get_brand_memory),
    prompt: BuiltPrompt = Depends(get_built_prompt),
) -> HTMLResponse:
    brief = topic_service.get_brief(request)
    return _render(
        request,
        memory=memory,
        prompt=prompt,
        values=topic_service.brief_form_values(brief),
        ready=bool(ready) and brief is not None,
        generated=bool(generated),
    )


@router.post("/compose", response_model=None)
def capture_brief(
    request: Request,
    memory: BrandMemory = Depends(get_brand_memory),
    prompt: BuiltPrompt = Depends(get_built_prompt),
    topic: str = Form(""),
    platform: str = Form(""),
) -> Response:
    raw = {"topic": topic, "platform": platform}
    try:
        payload = TopicBrief.model_validate(raw)
    except ValidationError as exc:
        return _render(
            request,
            memory=memory,
            prompt=prompt,
            values={**EMPTY_BRIEF, **raw},
            errors=_friendly_errors(exc),
        )

    topic_service.save_brief(request, payload)
    return RedirectResponse(url="/compose?ready=1", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/api/brief")
def read_brief(request: Request) -> dict[str, object]:
    return topic_service.brief_payload(topic_service.get_brief(request))
