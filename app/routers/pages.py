from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import get_settings
from app.database import ping_database
from app.templating import build_template_context, templates

router = APIRouter(tags=["pages"])


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    settings = get_settings()
    context = build_template_context(
        request=request,
        page_title="Studio",
        database_ok=ping_database(),
        groq_configured=settings.groq_configured,
        openai_configured=settings.openai_configured,
    )
    return templates.TemplateResponse(request, "index.html", context)
