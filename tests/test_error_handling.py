import uuid

from fastapi.testclient import TestClient

from apps.api.main import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def _assert_error_response(response, expected_status: int, expected_code: str, expected_message: str):
    assert response.status_code == expected_status
    payload = response.json()

    assert payload["error"]["code"] == expected_code
    assert payload["error"]["message"] == expected_message

    request_id = payload["error"].get("request_id")
    assert request_id
    uuid.UUID(request_id)


def test_not_found_error_response():
    with _client() as client:
        response = client.get("/missing")

    _assert_error_response(response, 404, "HTTP_404", "Not Found")


def test_validation_error_response():
    with _client() as client:
        response = client.get("/echo-int", params={"value": "abc"})

    _assert_error_response(response, 422, "HTTP_422", "Validation Error")


def test_internal_server_error_response(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")
    with TestClient(create_app(), raise_server_exceptions=False) as client:
        response = client.get("/__test__/raise")

    _assert_error_response(response, 500, "HTTP_500", "Internal Server Error")
