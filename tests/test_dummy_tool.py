"""Example-level tests for DummyTool reference implementation."""

from __future__ import annotations

import json

import pytest

from packages.core.tools import ToolContext
from packages.core.tools.examples import DummyTool


@pytest.fixture()
def dummy_tool() -> DummyTool:
    return DummyTool()


def test_dummy_tool_success(dummy_tool: DummyTool) -> None:
    context = ToolContext(
        trace_id="trace-success-001",
        agent_id="agent-example",
        params={"message": "hello", "count": 3},
    )

    result = dummy_tool.run(context)

    assert result.ok is True
    assert result.error is None
    assert result.trace_id == "trace-success-001"
    assert result.tool_name == "dummy.echo"
    assert result.data == {"message": "hello", "count": 3}


def test_dummy_tool_error_when_params_empty(dummy_tool: DummyTool) -> None:
    context = ToolContext(
        trace_id="trace-error-002",
        agent_id="agent-example",
        params={},
    )

    result = dummy_tool.run(context)

    assert result.ok is False
    assert result.data is None
    assert result.trace_id == "trace-error-002"
    assert result.tool_name == "dummy.echo"
    assert result.error is not None
    assert result.error.code == "EMPTY_PARAMS"
    assert result.error.message == "No params provided"
    assert result.error.retryable is False


def test_dummy_tool_result_serializable(dummy_tool: DummyTool) -> None:
    context = ToolContext(
        trace_id="trace-serialize-003",
        agent_id="agent-example",
        params={"ping": "pong"},
    )

    result = dummy_tool.run(context)
    serialized = result.model_dump()

    # Ensure JSON-safe serialization
    json_string = json.dumps(serialized)
    assert json.loads(json_string) == {
        "ok": True,
        "data": {"ping": "pong"},
        "error": None,
        "trace_id": "trace-serialize-003",
        "tool_name": "dummy.echo",
    }


def test_dummy_tool_propagates_trace_id(dummy_tool: DummyTool) -> None:
    context = ToolContext(
        trace_id="trace-propagate-004",
        agent_id="agent-example",
        params={"foo": "bar"},
    )

    result = dummy_tool.run(context)

    assert result.trace_id == context.trace_id
