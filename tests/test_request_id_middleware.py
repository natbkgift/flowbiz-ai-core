from __future__ import annotations

from typing import TYPE_CHECKING

import uuid

from apps.api.main import app
from tests._requires import requires_httpx

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

pytestmark = [requires_httpx]


def _client() -> TestClient:
    from fastapi.testclient import TestClient

    return TestClient(app)


def test_response_contains_generated_request_id():
    with _client() as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert uuid.UUID(response.headers["X-Request-ID"]).version == 4


def test_request_id_header_is_reused_when_valid():
    request_id = str(uuid.uuid4())

    with _client() as client:
        response = client.get("/", headers={"X-Request-ID": request_id})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id


def test_logging_captures_request_id_from_context(caplog):
    request_id = str(uuid.uuid4())

    with _client() as client:
        response = client.get("/log", headers={"X-Request-ID": request_id})

    assert response.status_code == 200
    assert f"request_id={request_id}" in caplog.text
