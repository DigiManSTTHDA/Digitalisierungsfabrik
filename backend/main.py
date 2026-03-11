"""FastAPI application entry point."""

from fastapi import FastAPI

from api.router import router
from config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(router, prefix=settings.api_prefix)
    return app


app = create_app()
