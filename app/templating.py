from pathlib import Path

from fastapi.templating import Jinja2Templates

from app import __version__
from app.config import get_settings

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def build_template_context(**extra: object) -> dict[str, object]:
    settings = get_settings()
    context: dict[str, object] = {
        "app_name": settings.app_name,
        "app_env": settings.app_env,
        "app_version": __version__,
        "debug": settings.debug,
    }
    context.update(extra)
    return context
