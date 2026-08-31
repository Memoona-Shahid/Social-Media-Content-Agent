from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.config import get_settings
from app.database import ensure_database_dir
from app.routers import health, pages

APP_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_database_dir()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url=None,
    )
    application.mount(
        "/static",
        StaticFiles(directory=APP_DIR / "static"),
        name="static",
    )
    application.include_router(health.router)
    application.include_router(pages.router)
    return application


app = create_app()
