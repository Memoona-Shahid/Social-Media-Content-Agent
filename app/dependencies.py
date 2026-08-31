from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.memory_service import (
    BrandMemory,
    MemoryNotLoadedError,
    ensure_loaded,
    load_brand_memory,
)
from app.services.prompt_builder import BuiltPrompt, build_prompt
from app.services.topic_service import get_brief


def get_brand_memory(db: Session = Depends(get_db)) -> BrandMemory:
    """Load the saved brand voice for this request.

    Use this dependency on every generation endpoint so content is written
    in the current profile, not a stale in-memory copy.
    """
    return load_brand_memory(db)


def require_brand_memory(
    memory: BrandMemory = Depends(get_brand_memory),
) -> BrandMemory:
    try:
        return ensure_loaded(memory)
    except MemoryNotLoadedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


def get_built_prompt(
    request: Request,
    memory: BrandMemory = Depends(get_brand_memory),
) -> BuiltPrompt:
    """Compile topic, platform, and brand memory into a structured prompt."""
    return build_prompt(memory, get_brief(request))


def require_built_prompt(
    prompt: BuiltPrompt = Depends(get_built_prompt),
) -> BuiltPrompt:
    if prompt.ready:
        return prompt
    missing = ", ".join(prompt.missing) or "brief and memory"
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"Prompt is not ready. Missing {missing}.",
    )
