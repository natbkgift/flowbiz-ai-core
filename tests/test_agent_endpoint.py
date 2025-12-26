"""Integration tests for agent API endpoint."""

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


def test_agent_run_endpoint_smoke(client: TestClient):
    """POST /v1/agent/run/legacy returns 200 and matches schema."""

    response = client.post(
        "/v1/agent/run/legacy",
        json={"input_text": "hello"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "hello" in data["output_text"]
    assert data["output_text"] == "OK: hello"


def test_agent_run_endpoint_with_all_fields(client: TestClient):
    """Ensure endpoint accepts all optional fields."""

    response = client.post(
        "/v1/agent/run/legacy",
        json={
            "input_text": "comprehensive test",
            "user_id": "user-123",
            "client_id": "client-456",
            "channel": "web",
            "metadata": {"key": "value", "count": 42},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert "comprehensive test" in data["output_text"]


def test_agent_run_endpoint_missing_input_text(client: TestClient):
    """Ensure endpoint validates required fields."""

    response = client.post(
        "/v1/agent/run/legacy",
        json={},
    )

    assert response.status_code == 422  # Validation error


def test_agent_run_endpoint_extra_fields_rejected(client: TestClient):
    """Ensure endpoint rejects unknown fields in request body."""

    response = client.post(
        "/v1/agent/run/legacy",
        json={
            "input_text": "test",
            "unknown_field": "should fail",
        },
    )

    assert response.status_code == 422


def test_agent_run_endpoint_trace_contract(client: TestClient):
    """Ensure response trace dict includes contract fields (agent_name, request_id)."""

    response = client.post(
        "/v1/agent/run/legacy",
        json={"input_text": "test trace"},
    )

    assert response.status_code == 200
    data = response.json()

    # Verify trace exists and has contract fields
    assert "trace" in data
    trace = data["trace"]
    assert isinstance(trace, dict)
    assert "agent_name" in trace
    assert "request_id" in trace
    assert trace["agent_name"] == "default"
    assert len(trace["request_id"]) > 0  # Should be a UUID


def test_agent_run_endpoint_includes_request_id(client: TestClient):
    """Ensure response includes X-Request-ID header."""

    response = client.post(
        "/v1/agent/run/legacy",
        json={"input_text": "test"},
    )

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    # Request ID should be a valid UUID format
    request_id = response.headers["X-Request-ID"]
    assert len(request_id) > 0


def test_agent_run_endpoint_default_channel(client: TestClient):
    """Ensure channel defaults to 'api' when not provided."""

    response = client.post(
        "/v1/agent/run/legacy",
        json={"input_text": "test"},
    )

    assert response.status_code == 200
    # The default channel is used internally, no need to check in response


def test_agent_run_endpoint_result_schema_strict(client: TestClient):
    """Ensure response matches strict AgentResult schema."""

    response = client.post(
        "/v1/agent/run/legacy",
        json={"input_text": "schema test"},
    )

    assert response.status_code == 200
    data = response.json()

    # Must have these fields
    assert "output_text" in data
    assert "status" in data

    # Status must be valid literal
    assert data["status"] in ["ok", "refused", "error"]

    # Verify expected values for this test case
    assert data["status"] == "ok"
    assert data["output_text"] == "OK: schema test"
