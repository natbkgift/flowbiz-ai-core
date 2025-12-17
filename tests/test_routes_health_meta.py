from fastapi.testclient import TestClient
import os
import pytest

from apps.api.main import app
from packages.core import get_settings


@pytest.fixture
def client() -> TestClient:
    """Provides a TestClient instance for the API."""

    return TestClient(app)


def test_health_endpoint_returns_status(client: TestClient):
    """Ensure the health check reports expected fields."""

    response = client.get("/healthz")
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "ok"
    assert data["service"] == get_settings().name
    assert data["version"] == os.getenv("APP_VERSION") or "dev"


def test_meta_endpoint_returns_env(client: TestClient):
    """Ensure the meta endpoint reports service name and environment."""

    settings = get_settings()
    response = client.get("/v1/meta")
    data = response.json()

    assert response.status_code == 200
    assert data["service"] == settings.name
    assert data["env"] == settings.env
