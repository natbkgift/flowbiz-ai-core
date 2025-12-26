"""Tests for PR-022 Agent Runtime Skeleton."""

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
    """Create test client for API."""
    from fastapi.testclient import TestClient

    return TestClient(app)


def test_agent_run_echo_golden_path(client: TestClient):
    """POST /v1/agent/run with agent=echo returns ok with echoed input."""

    response = client.post(
        "/v1/agent/run",
        json={
            "agent": "echo",
            "input": "hello",
            "meta": {"trace_id": "test-trace-123", "mode": "dev"},
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["agent"] == "echo"
    assert data["output"] == "hello"
    assert data["trace_id"] == "test-trace-123"
    assert data["errors"] == []


def test_agent_run_echo_output_equals_input(client: TestClient):
    """Verify echo agent output exactly matches input."""

    test_input = "this is a test message"

    response = client.post(
        "/v1/agent/run",
        json={"agent": "echo", "input": test_input},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["output"] == test_input


def test_agent_run_trace_id_generated_if_missing(client: TestClient):
    """Verify trace_id is generated when not provided in request."""

    response = client.post(
        "/v1/agent/run",
        json={"agent": "echo", "input": "test"},
    )

    assert response.status_code == 200
    data = response.json()

    assert "trace_id" in data
    assert len(data["trace_id"]) > 0
    # Should be UUID format
    assert "-" in data["trace_id"]


def test_agent_run_trace_id_preserved(client: TestClient):
    """Verify provided trace_id is preserved in response."""

    custom_trace_id = "custom-trace-abc-123"

    response = client.post(
        "/v1/agent/run",
        json={
            "agent": "echo",
            "input": "test",
            "meta": {"trace_id": custom_trace_id},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["trace_id"] == custom_trace_id


def test_agent_run_unknown_agent_returns_error(client: TestClient):
    """POST /v1/agent/run with unknown agent returns AGENT_NOT_FOUND error."""

    response = client.post(
        "/v1/agent/run",
        json={"agent": "unknown-agent", "input": "test"},
    )

    assert response.status_code == 200  # Not 404, returns 200 with error status

    data = response.json()
    assert data["status"] == "error"
    assert data["agent"] == "unknown-agent"
    assert data["output"] is None
    assert len(data["errors"]) == 1

    error = data["errors"][0]
    assert error["code"] == "AGENT_NOT_FOUND"
    assert "unknown-agent" in error["message"]


def test_agent_run_missing_agent_field(client: TestClient):
    """Verify missing required 'agent' field returns validation error."""

    response = client.post(
        "/v1/agent/run",
        json={"input": "test"},
    )

    assert response.status_code == 422  # FastAPI validation error


def test_agent_run_missing_input_field(client: TestClient):
    """Verify missing required 'input' field returns validation error."""

    response = client.post(
        "/v1/agent/run",
        json={"agent": "echo"},
    )

    assert response.status_code == 422  # FastAPI validation error


def test_agent_run_empty_request_body(client: TestClient):
    """Verify empty request body returns validation error."""

    response = client.post(
        "/v1/agent/run",
        json={},
    )

    assert response.status_code == 422


def test_agent_run_extra_fields_rejected(client: TestClient):
    """Verify extra fields in request are rejected (strict schema)."""

    response = client.post(
        "/v1/agent/run",
        json={
            "agent": "echo",
            "input": "test",
            "unknown_field": "should fail",
        },
    )

    assert response.status_code == 422


def test_agent_run_response_schema_strict(client: TestClient):
    """Verify response matches exact PR-022 contract keys."""

    response = client.post(
        "/v1/agent/run",
        json={"agent": "echo", "input": "schema test"},
    )

    assert response.status_code == 200
    data = response.json()

    # Must have exactly these fields
    expected_keys = {"status", "trace_id", "agent", "output", "errors"}
    assert set(data.keys()) == expected_keys


def test_agent_run_meta_defaults(client: TestClient):
    """Verify meta field is optional with defaults."""

    response = client.post(
        "/v1/agent/run",
        json={"agent": "echo", "input": "test"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"


def test_agent_run_non_string_input_validation(client: TestClient):
    """Verify non-string input is rejected by validation."""

    response = client.post(
        "/v1/agent/run",
        json={"agent": "echo", "input": 123},  # Number instead of string
    )

    assert response.status_code == 422


def test_agent_run_error_response_structure(client: TestClient):
    """Verify error response has correct structure with error code and message."""

    response = client.post(
        "/v1/agent/run",
        json={"agent": "nonexistent", "input": "test"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "error"
    assert isinstance(data["errors"], list)
    assert len(data["errors"]) > 0

    error = data["errors"][0]
    assert "code" in error
    assert "message" in error
    assert "details" in error
    assert error["code"] in ["VALIDATION_ERROR", "AGENT_NOT_FOUND", "RUNTIME_ERROR"]
