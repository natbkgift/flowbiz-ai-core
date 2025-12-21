from __future__ import annotations

from typing import TYPE_CHECKING

import logging
import uuid

from apps.api.main import app
from tests._requires import requires_httpx

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

pytestmark = [requires_httpx]


def _client() -> TestClient:
    from fastapi.testclient import TestClient

    return TestClient(app)


def _find_request_log(caplog):
    for record in caplog.records:
        if "request completed" in record.getMessage():
            return record
    raise AssertionError("request log not found")


def test_request_logging_includes_fields(caplog):
    caplog.set_level(logging.INFO)
    request_id = str(uuid.uuid4())

    with _client() as client:
        response = client.get("/", headers={"X-Request-ID": request_id})

    assert response.status_code == 200
    record = _find_request_log(caplog)

    assert record.method == "GET"
    assert record.path == "/"
    assert record.status == 200
    assert record.duration_ms >= 0
    assert record.request_id == request_id


def test_not_found_request_is_logged_as_warning(caplog):
    caplog.set_level(logging.WARNING)

    with _client() as client:
        response = client.get("/missing")

    assert response.status_code == 404
    record = _find_request_log(caplog)

    assert record.status == 404
    assert record.levelname == "WARNING"
