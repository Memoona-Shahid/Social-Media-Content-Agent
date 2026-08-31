from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app import __version__
from app.config import get_settings
from app.database import init_db
from app.routers import generate, health, memory, pages, profile, prompt, topic

APP_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
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
    application.include_router(profile.router)
    application.include_router(memory.router)
    application.include_router(topic.router)
    application.include_router(prompt.router)
    application.include_router(generate.router)
    application.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie="ca_session",
        same_site="lax",
    )
    return application


app = create_app()
