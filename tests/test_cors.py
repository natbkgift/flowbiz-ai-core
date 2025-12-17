from fastapi.testclient import TestClient

from apps.api.main import create_app


def test_cors_simple_request_reflects_allowed_origin(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_CORS_ALLOW_ORIGINS", "https://example.com")

    app = create_app()
    client = TestClient(app)

    resp = client.get("/healthz", headers={"Origin": "https://example.com"})
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "https://example.com"


def test_cors_preflight_options(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_CORS_ALLOW_ORIGINS", "https://example.com")

    app = create_app()
    client = TestClient(app)

    resp = client.options(
        "/healthz",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.status_code in (200, 204)
    assert resp.headers.get("access-control-allow-origin") == "https://example.com"
    methods = resp.headers.get("access-control-allow-methods", "")
    returned_methods = {method.strip() for method in methods.split(",")}
    expected_methods = {"GET", "POST", "PUT", "PATCH", "DELETE"}
    assert returned_methods == expected_methods
