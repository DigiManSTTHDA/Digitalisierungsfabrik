"""FastAPI application entry point.

Factory function creates and configures the app. Module-level `app` instance
is used by uvicorn and the test client.
"""

import structlog
from fastapi import FastAPI
from pydantic import BaseModel

from config import get_settings

logger = structlog.get_logger()


class HealthResponse(BaseModel):
    status: str


def create_app() -> FastAPI:
    settings = get_settings()

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(__import__("logging"), settings.log_level.upper(), 20)
        ),
    )

    application = FastAPI(
        title="Digitalisierungsfabrik API",
        description=(
            "AI-guided business process elicitation system. "
            "Backend for the Digitalisierungsfabrik prototype."
        ),
        version="0.1.0",
    )

    @application.get("/health", response_model=HealthResponse, tags=["meta"])
    async def health_check() -> HealthResponse:
        """Liveness probe — returns ok when the server is running."""
        return HealthResponse(status="ok")

    logger.info("app_created", log_level=settings.log_level)
    return application


app = create_app()
