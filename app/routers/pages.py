from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db, ping_database
from app.services import profile_service
from app.templating import build_template_context, templates

router = APIRouter(tags=["pages"])


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    settings = get_settings()
    context = build_template_context(
        request=request,
        page_title="Studio",
        active_nav="studio",
        database_ok=ping_database(),
        groq_configured=settings.groq_configured,
        openai_configured=settings.openai_configured,
        profile=profile_service.get_profile(db),
    )
    return templates.TemplateResponse(request, "index.html", context)
