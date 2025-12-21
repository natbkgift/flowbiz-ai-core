from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from apps.api.main import app
from packages.core import get_settings
from tests._requires import requires_httpx

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

pytestmark = [requires_httpx]


@pytest.fixture
def client() -> TestClient:
    from fastapi.testclient import TestClient

    return TestClient(app)


def test_health_endpoint_returns_status(client: "TestClient"):
    """Ensure the health check reports expected fields."""

    response = client.get("/healthz")
    data = response.json()

    assert response.status_code == 200
    assert data["status"] == "ok"
    assert data["service"] == get_settings().name


@pytest.mark.parametrize(
    "app_version,expected",
    [
        ("1.2.3", "1.2.3"),
        (None, "dev"),
    ],
)
def test_health_endpoint_version(
    client: "TestClient", monkeypatch: pytest.MonkeyPatch, app_version: str | None, expected: str
):
    """Ensure the health check reports the correct version."""

    if app_version is None:
        monkeypatch.delenv("APP_VERSION", raising=False)
    else:
        monkeypatch.setenv("APP_VERSION", app_version)

    response = client.get("/healthz")
    assert response.json()["version"] == expected


@pytest.mark.parametrize(
    "app_version,expected_version",
    [
        ("2.0.0", "2.0.0"),
        (None, "dev"),
    ],
)
def test_meta_endpoint_returns_env(
    client: "TestClient", monkeypatch: pytest.MonkeyPatch, app_version: str | None, expected_version: str
):
    """Ensure the meta endpoint reports service name, environment, and version."""

    settings = get_settings()
    if app_version is None:
        monkeypatch.delenv("APP_VERSION", raising=False)
    else:
        monkeypatch.setenv("APP_VERSION", app_version)

    response = client.get("/v1/meta")
    data = response.json()

    assert response.status_code == 200
    assert data["service"] == settings.name
    assert data["env"] == settings.env
    assert data["version"] == expected_version
