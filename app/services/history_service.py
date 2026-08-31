from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.history import GeneratedPost
from app.services.generator import GenerationResult

LIST_LIMIT = 100


def record_generation(
    db: Session,
    result: GenerationResult,
    *,
    voice_name: str = "",
) -> GeneratedPost:
    row = GeneratedPost(
        topic=result.topic,
        platform=result.platform,
        content=result.content,
        provider=result.provider,
        model=result.model,
        voice_name=voice_name,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_generations(db: Session, *, limit: int = LIST_LIMIT) -> list[GeneratedPost]:
    statement = (
        select(GeneratedPost)
        .order_by(GeneratedPost.created_at.desc(), GeneratedPost.id.desc())
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_generation_by_id(db: Session, post_id: int) -> GeneratedPost | None:
    return db.get(GeneratedPost, post_id)
