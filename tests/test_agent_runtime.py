"""Unit tests for agent runtime components."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.agents import AgentContext, AgentResult, AgentRuntime, DefaultAgent


def test_agent_context_create():
    """Ensure AgentContext is created with proper defaults and UTC timestamp."""

    ctx = AgentContext.create(
        input_text="hello",
        request_id="test-123",
        user_id="user-1",
        client_id="client-1",
        channel="test",
        metadata={"key": "value"},
    )

    assert ctx.input_text == "hello"
    assert ctx.request_id == "test-123"
    assert ctx.user_id == "user-1"
    assert ctx.client_id == "client-1"
    assert ctx.channel == "test"
    assert ctx.metadata == {"key": "value"}
    assert ctx.created_at is not None
    assert ctx.created_at.tzinfo is not None  # Must be timezone-aware


def test_agent_context_minimal():
    """Ensure AgentContext works with minimal required fields."""

    ctx = AgentContext.create(input_text="test")

    assert ctx.input_text == "test"
    assert ctx.request_id is None
    assert ctx.user_id is None
    assert ctx.client_id is None
    assert ctx.channel == "api"  # Default
    assert ctx.metadata == {}
    assert ctx.created_at is not None


def test_agent_result_strict_schema():
    """Ensure AgentResult rejects unknown fields (extras forbidden)."""

    # Valid result
    result = AgentResult(output_text="success", status="ok")
    assert result.output_text == "success"
    assert result.status == "ok"

    # Invalid - extra fields should be forbidden
    with pytest.raises(ValidationError) as exc_info:
        AgentResult(output_text="test", status="ok", unknown_field="should fail")

    assert "unknown_field" in str(exc_info.value)


def test_agent_result_status_validation():
    """Ensure AgentResult only accepts valid status values."""

    # Valid statuses
    AgentResult(output_text="ok", status="ok")
    AgentResult(output_text="refused", status="refused", reason="policy")
    AgentResult(output_text="error", status="error", reason="crash")

    # Invalid status
    with pytest.raises(ValidationError):
        AgentResult(output_text="invalid", status="invalid_status")


def test_default_agent_deterministic():
    """Ensure DefaultAgent produces deterministic echo-like output."""

    agent = DefaultAgent()
    ctx = AgentContext.create(input_text="hello world")

    result = agent.run(ctx)

    assert result.status == "ok"
    assert "hello world" in result.output_text
    assert result.output_text == "OK: hello world"
    assert result.reason is None
    # Verify trace contract fields (agent_name always present, request_id mirrors context)
    assert result.trace.get("agent_name") == "default"
    assert "request_id" in result.trace


def test_agent_runtime_default_agent_ok():
    """Call runtime directly and assert deterministic output."""

    runtime = AgentRuntime()
    result = runtime.run(
        input_text="test input",
        request_id="req-123",
        user_id="user-1",
        channel="api",
    )

    assert result.status == "ok"
    assert result.output_text == "OK: test input"


def test_agent_runtime_with_metadata():
    """Ensure runtime passes metadata through context."""

    runtime = AgentRuntime()
    result = runtime.run(
        input_text="metadata test",
        metadata={"foo": "bar", "count": 42},
    )

    assert result.status == "ok"
    assert "metadata test" in result.output_text


def test_agent_runtime_minimal():
    """Ensure runtime works with only required fields."""

    runtime = AgentRuntime()
    result = runtime.run(input_text="minimal")

    assert result.status == "ok"
    assert "minimal" in result.output_text
