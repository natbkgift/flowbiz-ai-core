from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from apps.api.main import app
from tests._requires import requires_httpx

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

pytestmark = [requires_httpx]


@pytest.fixture
def client() -> TestClient:
    from fastapi.testclient import TestClient

    return TestClient(app)


def test_root_endpoint_returns_placeholder_message(client: TestClient):
    """Tests that the root endpoint returns the expected placeholder message."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "FlowBiz AI Core API"}
