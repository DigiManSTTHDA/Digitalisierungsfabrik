from fastapi.testclient import TestClient

from config import Settings
from main import app


def test_health_endpoint_reports_ok() -> None:
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "digitalisierungsfabrik-backend"}


def test_settings_default_values() -> None:
    settings = Settings()

    assert settings.app_name == "digitalisierungsfabrik-backend"
    assert settings.api_prefix == "/api"
