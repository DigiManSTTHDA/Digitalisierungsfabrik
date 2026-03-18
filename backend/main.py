"""FastAPI application entry point.

Factory function creates and configures the app. Module-level `app` instance
is used by uvicorn and the test client.
"""

import logging
import logging.handlers

import structlog
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.router import router as api_router
from api.websocket import websocket_session
from config import get_settings

logger = structlog.get_logger()


class HealthResponse(BaseModel):
    status: str


def _configure_file_logging(log_file: str, log_level: int) -> None:
    """Attach a rotating file handler to the root logger when LOG_FILE is set."""
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB per file
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)


def create_app() -> FastAPI:
    settings = get_settings()

    log_level_int = getattr(logging, settings.log_level.upper(), logging.INFO)

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(log_level_int),
    )

    if settings.log_file:
        _configure_file_logging(settings.log_file, log_level_int)

    application = FastAPI(
        title="Digitalisierungsfabrik API",
        description=(
            "AI-guided business process elicitation system. "
            "Backend for the Digitalisierungsfabrik prototype."
        ),
        version="0.1.0",
    )

    # CORS — allow frontend dev server (HLA 2.2)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # REST routes
    application.include_router(api_router)

    # WebSocket route (HLA 3.2)
    @application.websocket("/ws/session/{project_id}")
    async def ws_session(websocket: WebSocket, project_id: str) -> None:
        await websocket_session(websocket, project_id)

    @application.get("/health", response_model=HealthResponse, tags=["meta"])
    async def health_check() -> HealthResponse:
        """Liveness probe — returns ok when the server is running."""
        return HealthResponse(status="ok")

    logger.info("app_created", log_level=settings.log_level)
    return application


app = create_app()
