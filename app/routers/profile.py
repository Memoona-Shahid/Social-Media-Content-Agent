from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.profile import ProfileInput
from app.services import profile_service
from app.templating import build_template_context, templates

router = APIRouter(tags=["profile"])


def _friendly_errors(exc: ValidationError) -> dict[str, str]:
    errors: dict[str, str] = {}
    for item in exc.errors():
        field = str(item.get("loc", ("form",))[0])
        message = item.get("msg", "Invalid value.")
        if message.startswith("Value error, "):
            message = message.removeprefix("Value error, ")
        elif "emoji_preference" in field:
            message = "Choose none, light, or frequent."
        elif "should have at most" in message:
            message = "This value is too long."
        errors[field] = message
    return errors


def _render(
    request: Request,
    *,
    profile,
    values: dict[str, str],
    errors: dict[str, str] | None = None,
    saved: bool = False,
) -> HTMLResponse:
    context = build_template_context(
        request=request,
        page_title="Brand Voice",
        active_nav="profile",
        profile=profile,
        values=values,
        errors=errors or {},
        saved=saved,
    )
    return templates.TemplateResponse(request, "profile.html", context)


@router.get("/profile", response_class=HTMLResponse)
def profile_page(
    request: Request,
    saved: int = 0,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    profile = profile_service.get_profile(db)
    return _render(
        request,
        profile=profile,
        values=profile_service.to_form_values(profile),
        saved=bool(saved),
    )


@router.post("/profile", response_model=None)
def save_profile(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(""),
    profession: str = Form(""),
    audience: str = Form(""),
    tone: str = Form(""),
    style: str = Form(""),
    emoji_preference: str = Form("none"),
    cta: str = Form(""),
    hashtags: str = Form(""),
) -> Response:
    raw = {
        "name": name,
        "profession": profession,
        "audience": audience,
        "tone": tone,
        "style": style,
        "emoji_preference": emoji_preference,
        "cta": cta,
        "hashtags": hashtags,
    }
    try:
        payload = ProfileInput.model_validate(raw)
    except ValidationError as exc:
        return _render(
            request,
            profile=profile_service.get_profile(db),
            values=raw,
            errors=_friendly_errors(exc),
        )

    profile_service.upsert_profile(db, payload)
    return RedirectResponse(url="/profile?saved=1", status_code=status.HTTP_303_SEE_OTHER)
