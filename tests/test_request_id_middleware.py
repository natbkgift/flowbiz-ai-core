import io
import logging
import uuid

from fastapi.testclient import TestClient

from apps.api.main import app
from packages.core.logging import LOG_FORMAT, RequestIdFormatter, get_logger


def _client() -> TestClient:
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


def test_logging_captures_request_id_from_context():
    logger = get_logger("flowbiz.api")
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(RequestIdFormatter(LOG_FORMAT))
    logger.addHandler(handler)

    request_id = str(uuid.uuid4())

    try:
        with _client() as client:
            response = client.get("/log", headers={"X-Request-ID": request_id})

        assert response.status_code == 200
        handler.flush()
        assert f"request_id={request_id}" in stream.getvalue()
    finally:
        logger.removeHandler(handler)
