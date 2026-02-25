"""Tests for PR-026 response contract schemas."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from packages.core.contracts.response import (
    AgentResponseEnvelope,
    ResponseError,
    ToolResponseEnvelope,
)


def test_response_error_defaults_and_immutability() -> None:
    error = ResponseError(code="E001", message="failed")
    assert error.details == {}
    assert error.retriable is False

    with pytest.raises((ValidationError, AttributeError)):
        error.message = "changed"  # type: ignore[misc]


def test_agent_response_envelope_ok_round_trip() -> None:
    envelope = AgentResponseEnvelope(
        status="ok",
        trace_id="trace-1",
        agent="echo",
        output="hello",
        metadata={"mode": "dev"},
    )

    dumped = envelope.model_dump()
    loaded = AgentResponseEnvelope.model_validate(dumped)
    assert loaded == envelope
    assert json.loads(json.dumps(dumped)) == dumped


def test_agent_response_envelope_error_with_errors() -> None:
    envelope = AgentResponseEnvelope(
        status="error",
        trace_id="trace-2",
        agent="echo",
        output=None,
        errors=[ResponseError(code="AGENT_NOT_FOUND", message="not found")],
    )

    assert envelope.status == "error"
    assert len(envelope.errors) == 1
    assert envelope.errors[0].code == "AGENT_NOT_FOUND"


def test_tool_response_envelope_accepts_structured_output() -> None:
    envelope = ToolResponseEnvelope(
        status="ok",
        trace_id="trace-3",
        tool="dummy",
        output={"value": 123, "items": ["a", "b"]},
    )

    assert envelope.status == "ok"
    assert envelope.tool == "dummy"
    assert envelope.output == {"value": 123, "items": ["a", "b"]}


def test_response_envelopes_reject_extra_fields() -> None:
    with pytest.raises(ValidationError):
        AgentResponseEnvelope(  # type: ignore[call-arg]
            status="ok",
            trace_id="trace-4",
            agent="echo",
            output="x",
            unknown_field="not-allowed",
        )

    with pytest.raises(ValidationError):
        ToolResponseEnvelope(  # type: ignore[call-arg]
            status="ok",
            trace_id="trace-5",
            tool="dummy",
            output={},
            extra="not-allowed",
        )
