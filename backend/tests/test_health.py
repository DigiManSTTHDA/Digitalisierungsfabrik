"""Smoke test: health-check endpoint.

This test is written BEFORE the implementation (TDD). It must fail first,
then pass once main.py is implemented.
"""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_health_returns_ok():
    """GET /health must return HTTP 200 with body {"status": "ok"}."""
    from main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_content_type_is_json():
    """GET /health must return application/json."""
    from main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")

    assert "application/json" in response.headers["content-type"]
