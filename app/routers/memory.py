from fastapi import APIRouter, Depends

from app.dependencies import get_brand_memory
from app.services.memory_service import BrandMemory

router = APIRouter(prefix="/api", tags=["memory"])


@router.get("/memory")
def read_memory(memory: BrandMemory = Depends(get_brand_memory)) -> dict[str, object]:
    return memory.to_dict()
