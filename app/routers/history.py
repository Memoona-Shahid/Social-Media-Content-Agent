from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import history_service
from app.templating import build_template_context, templates

router = APIRouter(tags=["history"])


@router.get("/history", response_class=HTMLResponse)
def history_page(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    posts = history_service.list_generations(db)
    context = build_template_context(
        request=request,
        page_title="History",
        active_nav="history",
        posts=posts,
    )
    return templates.TemplateResponse(request, "history.html", context)


@router.get("/history/{post_id}", response_class=HTMLResponse)
def history_detail(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    post = history_service.get_generation_by_id(db, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation not found.")
    context = build_template_context(
        request=request,
        page_title=post.topic,
        active_nav="history",
        post=post,
    )
    return templates.TemplateResponse(request, "history_detail.html", context)


@router.get("/api/history")
def history_collection(db: Session = Depends(get_db)) -> dict[str, object]:
    posts = history_service.list_generations(db)
    return {"count": len(posts), "items": [post.to_dict() for post in posts]}


@router.get("/api/history/{post_id}")
def history_item(post_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    post = history_service.get_generation_by_id(db, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation not found.")
    return post.to_dict()
