from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.config import get_settings
from app.database import ping_database
from app.dependencies import get_brand_memory
from app.services.memory_service import BrandMemory
from app.templating import build_template_context, templates

router = APIRouter(tags=["pages"])


@router.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    memory: BrandMemory = Depends(get_brand_memory),
) -> HTMLResponse:
    settings = get_settings()
    context = build_template_context(
        request=request,
        page_title="Studio",
        active_nav="studio",
        database_ok=ping_database(),
        groq_configured=settings.groq_configured,
        openai_configured=settings.openai_configured,
        memory=memory,
    )
    return templates.TemplateResponse(request, "index.html", context)
