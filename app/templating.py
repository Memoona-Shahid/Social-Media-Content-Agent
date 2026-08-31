from pathlib import Path

from fastapi.templating import Jinja2Templates

from app import __version__
from app.config import get_settings
from app.services import settings_service

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def build_template_context(**extra: object) -> dict[str, object]:
    settings = get_settings()
    prefs = settings_service.load_preferences()
    provider, ready, setup_message = settings_service.resolve_llm(prefs, settings)
    context: dict[str, object] = {
        "app_name": settings.app_name,
        "app_env": settings.app_env,
        "app_version": __version__,
        "debug": settings.debug,
        "active_nav": "",
        "theme": prefs.theme,
        "llm_provider": provider,
        "llm_ready": ready,
        "llm_setup_message": setup_message,
        "app_prefs": prefs,
    }
    context.update(extra)
    return context
