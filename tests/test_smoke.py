"""Light smoke tests — PR-044.

Quick sanity checks that verify critical endpoints respond within
acceptable timeframes and return well-formed JSON.
"""

from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient

from apps.api.main import create_app


@pytest.fixture()
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


class TestSmoke:
    """Smoke tests: every critical endpoint must respond < 1s."""

    ENDPOINTS = [
        ("GET", "/healthz"),
        ("GET", "/v1/meta"),
        ("GET", "/v1/agent/tools"),
        ("GET", "/v1/agent/health"),
        ("GET", "/"),
    ]

    @pytest.mark.parametrize("method,path", ENDPOINTS)
    def test_endpoint_responds_fast(
        self, client: TestClient, method: str, path: str
    ) -> None:
        start = time.monotonic()
        r = getattr(client, method.lower())(path)
        elapsed = time.monotonic() - start
        assert r.status_code == 200, f"{method} {path} returned {r.status_code}"
        assert elapsed < 1.0, f"{method} {path} took {elapsed:.3f}s"

    @pytest.mark.parametrize("method,path", ENDPOINTS)
    def test_endpoint_returns_json(
        self, client: TestClient, method: str, path: str
    ) -> None:
        r = getattr(client, method.lower())(path)
        assert r.headers.get("content-type", "").startswith("application/json")
        r.json()  # must not raise

    def test_echo_agent_smoke(self, client: TestClient) -> None:
        start = time.monotonic()
        r = client.post(
            "/v1/agent/run",
            json={
                "agent": "echo",
                "input": "smoke test",
                "meta": {"trace_id": "smoke-001", "mode": "sync"},
            },
        )
        elapsed = time.monotonic() - start
        assert r.status_code == 200
        assert elapsed < 2.0
        data = r.json()
        assert data["status"] == "ok"


class TestSmokeHeaders:
    """Verify essential response headers."""

    def test_healthz_has_content_type(self, client: TestClient) -> None:
        r = client.get("/healthz")
        assert "application/json" in r.headers.get("content-type", "")

    def test_request_id_propagated(self, client: TestClient) -> None:
        import uuid

        custom_id = str(uuid.uuid4())
        r = client.get("/healthz", headers={"X-Request-ID": custom_id})
        assert r.headers.get("X-Request-ID") == custom_id
