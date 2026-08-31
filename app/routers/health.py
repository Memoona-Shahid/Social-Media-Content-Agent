from fastapi import APIRouter, Depends

from app import __version__
from app.config import get_settings
from app.database import ping_database
from app.dependencies import get_brand_memory
from app.services.memory_service import BrandMemory

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(memory: BrandMemory = Depends(get_brand_memory)) -> dict[str, object]:
    settings = get_settings()
    database_ok = ping_database()

    return {
        "status": "ok" if database_ok else "degraded",
        "app": settings.app_name,
        "version": __version__,
        "environment": settings.app_env,
        "database": "connected" if database_ok else "unreachable",
        "memory": "loaded" if memory.loaded else "empty",
        "llm": {
            "provider": settings.active_provider,
            "ready": settings.llm_ready,
        },
        "providers": {
            "groq": settings.groq_configured,
            "openai": settings.openai_configured,
        },
    }
