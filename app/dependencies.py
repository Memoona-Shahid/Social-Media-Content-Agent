from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.memory_service import (
    BrandMemory,
    MemoryNotLoadedError,
    ensure_loaded,
    load_brand_memory,
)


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
