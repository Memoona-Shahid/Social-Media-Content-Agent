from fastapi import APIRouter

from app import __version__
from app.config import get_settings
from app.database import ping_database

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, object]:
    settings = get_settings()
    database_ok = ping_database()

    return {
        "status": "ok" if database_ok else "degraded",
        "app": settings.app_name,
        "version": __version__,
        "environment": settings.app_env,
        "database": "connected" if database_ok else "unreachable",
        "providers": {
            "groq": settings.groq_configured,
            "openai": settings.openai_configured,
        },
    }
