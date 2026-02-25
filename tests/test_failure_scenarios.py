"""Failure scenario tests — PR-043.

Validates that the system returns proper error responses when things go wrong:
  - Unknown agent
  - Invalid request body
  - Disabled agent
  - Missing fields
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from apps.api.main import create_app


@pytest.fixture()
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


# ── Agent Not Found ──────────────────────────────────────────


class TestAgentNotFound:
    def test_unknown_agent_returns_error(self, client: TestClient) -> None:
        r = client.post(
            "/v1/agent/run",
            json={
                "agent": "nonexistent-agent",
                "input": "hello",
                "meta": {"trace_id": "fail-001", "mode": "sync"},
            },
        )
        assert r.status_code == 200  # runtime wraps errors in result
        data = r.json()
        assert data["status"] == "error"
        assert any(
            "AGENT_NOT_FOUND" in (e.get("code", "") or "")
            for e in data.get("errors", [])
        )


# ── Validation Errors ────────────────────────────────────────


class TestValidationErrors:
    def test_missing_agent_field(self, client: TestClient) -> None:
        r = client.post(
            "/v1/agent/run",
            json={"input": "hello", "meta": {"trace_id": "t", "mode": "sync"}},
        )
        assert r.status_code == 422

    def test_missing_input_field(self, client: TestClient) -> None:
        r = client.post(
            "/v1/agent/run",
            json={"agent": "echo", "meta": {"trace_id": "t", "mode": "sync"}},
        )
        assert r.status_code == 422

    def test_missing_meta_uses_defaults(self, client: TestClient) -> None:
        """meta has a default_factory so omitting it is valid."""
        r = client.post(
            "/v1/agent/run",
            json={"agent": "echo", "input": "hi"},
        )
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_empty_json_body(self, client: TestClient) -> None:
        r = client.post("/v1/agent/run", json={})
        assert r.status_code == 422

    def test_no_body(self, client: TestClient) -> None:
        r = client.post("/v1/agent/run")
        assert r.status_code == 422


# ── Invalid Routes ───────────────────────────────────────────


class TestInvalidRoutes:
    def test_nonexistent_route(self, client: TestClient) -> None:
        r = client.get("/v1/does-not-exist")
        assert r.status_code == 404

    def test_wrong_method_on_agent_run(self, client: TestClient) -> None:
        r = client.get("/v1/agent/run")
        assert r.status_code == 405

    def test_wrong_method_on_healthz(self, client: TestClient) -> None:
        r = client.post("/healthz")
        assert r.status_code == 405


# ── Echo Int Validation ──────────────────────────────────────


class TestEchoIntValidation:
    def test_non_integer_value(self, client: TestClient) -> None:
        r = client.get("/echo-int", params={"value": "abc"})
        assert r.status_code == 422

    def test_missing_value(self, client: TestClient) -> None:
        r = client.get("/echo-int")
        assert r.status_code == 422
