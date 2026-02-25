"""Golden-path integration tests — PR-042.

Validates the happy path through the full stack:
  API → Runtime → Agent → Response
  API → ToolRegistry → Snapshot
  API → AgentHealth → Status
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from apps.api.main import create_app


@pytest.fixture()
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


# ── Health & Meta ─────────────────────────────────────────────


class TestGoldenHealth:
    def test_healthz(self, client: TestClient) -> None:
        r = client.get("/healthz")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"

    def test_meta(self, client: TestClient) -> None:
        r = client.get("/v1/meta")
        assert r.status_code == 200
        data = r.json()
        assert "service" in data
        assert "version" in data


# ── Agent Run (echo agent) ───────────────────────────────────


class TestGoldenAgentRun:
    def test_echo_agent_success(self, client: TestClient) -> None:
        r = client.post(
            "/v1/agent/run",
            json={
                "agent": "echo",
                "input": "hello world",
                "meta": {"trace_id": "test-golden-001", "mode": "sync"},
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["agent"] == "echo"
        assert "hello world" in data["output"]

    def test_echo_agent_empty_input(self, client: TestClient) -> None:
        r = client.post(
            "/v1/agent/run",
            json={
                "agent": "echo",
                "input": "",
                "meta": {"trace_id": "test-golden-002", "mode": "sync"},
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"


# ── Agent Tools endpoint ─────────────────────────────────────


class TestGoldenAgentTools:
    def test_list_tools_returns_snapshot(self, client: TestClient) -> None:
        r = client.get("/v1/agent/tools")
        assert r.status_code == 200
        data = r.json()
        assert "tools" in data
        assert isinstance(data["tools"], list)

    def test_list_tools_with_disabled(self, client: TestClient) -> None:
        r = client.get("/v1/agent/tools", params={"include_disabled": True})
        assert r.status_code == 200
        assert "tools" in r.json()


# ── Agent Health endpoint ─────────────────────────────────────


class TestGoldenAgentHealth:
    def test_agent_health(self, client: TestClient) -> None:
        r = client.get("/v1/agent/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "registered_agents" in data
        assert "registered_tools" in data

    def test_agent_health_counts_are_nonnegative(self, client: TestClient) -> None:
        r = client.get("/v1/agent/health")
        data = r.json()
        assert data["registered_agents"] >= 0
        assert data["registered_tools"] >= 0


# ── Root & Misc ───────────────────────────────────────────────


class TestGoldenMisc:
    def test_root(self, client: TestClient) -> None:
        r = client.get("/")
        assert r.status_code == 200
        assert "message" in r.json()
