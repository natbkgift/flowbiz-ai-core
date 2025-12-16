from fastapi.testclient import TestClient
import pytest

from apps.api.main import app


@pytest.fixture
def client() -> TestClient:
    """Provides a TestClient instance for the API."""
    return TestClient(app)


def test_root_endpoint_returns_placeholder_message(client: TestClient):
    """Tests that the root endpoint returns the expected placeholder message."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "FlowBiz AI Core API"}
