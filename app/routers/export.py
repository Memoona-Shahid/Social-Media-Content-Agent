from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_brand_memory
from app.services import export_service, history_service
from app.services.export_service import ALLOWED_FORMATS, MEDIA_TYPES
from app.services.generator import get_generation
from app.services.memory_service import BrandMemory

router = APIRouter(tags=["export"])


def _file_response(document, fmt: str) -> Response:
    if fmt not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export format must be txt, md, or pdf.",
        )
    payload = export_service.render_export(document, fmt)
    filename = export_service.download_filename(document.topic, fmt)
    return Response(
        content=payload,
        media_type=MEDIA_TYPES[fmt],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/{fmt}")
def export_current_draft(
    request: Request,
    fmt: str,
    memory: BrandMemory = Depends(get_brand_memory),
) -> Response:
    generation = get_generation(request.session)
    if generation is None or not generation.content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No draft to export. Generate a post first.",
        )
    document = export_service.document_from_generation(
        generation,
        voice_name=memory.name,
    )
    return _file_response(document, fmt)


@router.get("/history/{post_id}/export/{fmt}")
def export_history_item(
    post_id: int,
    fmt: str,
    db: Session = Depends(get_db),
) -> Response:
    post = history_service.get_generation_by_id(db, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found.",
        )
    document = export_service.document_from_history(post)
    return _file_response(document, fmt)
