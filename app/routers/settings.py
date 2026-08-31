from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas.settings import LLM_OPTIONS, THEME_OPTIONS, SettingsInput
from app.schemas.topic import PLATFORM_OPTIONS
from app.services import settings_service
from app.templating import build_template_context, templates

router = APIRouter(tags=["settings"])


def _friendly_errors(exc: ValidationError) -> dict[str, str]:
    errors: dict[str, str] = {}
    for item in exc.errors():
        field = str(item.get("loc", ("form",))[0])
        if field == "default_platform":
            errors[field] = "Choose LinkedIn, X, Instagram, or Threads."
        elif field == "llm_provider":
            errors[field] = "Choose Groq or OpenAI."
        elif field == "theme":
            errors[field] = "Choose light or dark."
        else:
            errors[field] = item.get("msg", "Invalid value.")
    return errors


def _render(
    request: Request,
    *,
    values: dict[str, str],
    errors: dict[str, str] | None = None,
    saved: bool = False,
) -> HTMLResponse:
    settings = get_settings()
    context = build_template_context(
        request=request,
        page_title="Settings",
        active_nav="settings",
        values=values,
        errors=errors or {},
        saved=saved,
        platforms=PLATFORM_OPTIONS,
        llm_options=LLM_OPTIONS,
        theme_options=THEME_OPTIONS,
        groq_configured=settings.groq_configured,
        openai_configured=settings.openai_configured,
    )
    return templates.TemplateResponse(request, "settings.html", context)


@router.get("/settings", response_class=HTMLResponse)
def settings_page(
    request: Request,
    saved: int = 0,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    prefs = settings_service.get_preferences(db)
    return _render(
        request,
        values=prefs.to_form_values(),
        saved=bool(saved),
    )


@router.post("/settings", response_model=None)
def save_settings(
    request: Request,
    db: Session = Depends(get_db),
    default_platform: str = Form(""),
    llm_provider: str = Form(""),
    theme: str = Form(""),
) -> Response:
    raw = {
        "default_platform": default_platform,
        "llm_provider": llm_provider,
        "theme": theme,
    }
    try:
        payload = SettingsInput.model_validate(raw)
    except ValidationError as exc:
        return _render(
            request,
            values=raw,
            errors=_friendly_errors(exc),
        )

    settings_service.upsert_preferences(db, payload)
    return RedirectResponse(url="/settings?saved=1", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/api/settings")
def read_settings(db: Session = Depends(get_db)) -> dict[str, object]:
    prefs = settings_service.get_preferences(db)
    provider, ready, message = settings_service.resolve_llm(prefs)
    return {
        **prefs.to_dict(),
        "llm_ready": ready,
        "llm_setup_message": message,
        "resolved_provider": provider,
    }
