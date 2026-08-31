from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.dependencies import get_brand_memory
from app.services.generator import get_generation, pop_generation_error
from app.services.memory_service import BrandMemory
from app.services.topic_service import platform_label
from app.templating import build_template_context, templates

router = APIRouter(tags=["output"])


@router.get("/output", response_class=HTMLResponse)
def output_page(
    request: Request,
    generated: int = 0,
    memory: BrandMemory = Depends(get_brand_memory),
) -> HTMLResponse:
    generation = get_generation(request.session)
    context = build_template_context(
        request=request,
        page_title="Output",
        active_nav="output",
        memory=memory,
        generation=generation,
        platform_label=platform_label(generation.platform) if generation else "",
        generate_error=pop_generation_error(request.session),
        generated=bool(generated) and generation is not None,
    )
    return templates.TemplateResponse(request, "output.html", context)
