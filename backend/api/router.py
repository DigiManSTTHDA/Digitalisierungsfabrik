"""REST API routes."""

from fastapi import APIRouter

from config import get_settings

router = APIRouter()


@router.get("/health")
def read_health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "app": settings.app_name}
