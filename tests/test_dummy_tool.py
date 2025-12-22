"""Tests for DummyTool example implementation."""

from __future__ import annotations

import json

from packages.core.tools import ToolContext
from packages.core.tools.examples import DummyTool


def test_dummy_tool_success_with_params():
    """Test successful execution when params are provided."""
    tool = DummyTool()
    context = ToolContext(
        trace_id="trace-dummy-001",
        agent_id="agent-test",
        params={"key1": "value1", "key2": 42, "nested": {"inner": "data"}},
    )

    result = tool.run(context)

    assert result.ok is True
    assert result.error is None
    assert result.trace_id == "trace-dummy-001"
    assert result.tool_name == "dummy.echo"
    assert result.data is not None
    assert "echoed" in result.data
    assert result.data["echoed"] == {
        "key1": "value1",
        "key2": 42,
        "nested": {"inner": "data"},
    }


def test_dummy_tool_error_empty_params():
    """Test error path when params are empty."""
    tool = DummyTool()
    context = ToolContext(
        trace_id="trace-dummy-002",
        agent_id="agent-test",
        params={},
    )

    result = tool.run(context)

    assert result.ok is False
    assert result.data is None
    assert result.trace_id == "trace-dummy-002"
    assert result.tool_name == "dummy.echo"
    assert result.error is not None
    assert result.error.code == "EMPTY_PARAMS"
    assert result.error.message == "No params provided"
    assert result.error.retryable is False


def test_dummy_tool_trace_id_propagation():
    """Test that trace_id is correctly propagated to result."""
    tool = DummyTool()
    test_trace_id = "custom-trace-xyz-789"
    context = ToolContext(
        trace_id=test_trace_id,
        agent_id="agent-test",
        params={"test": "data"},
    )

    result = tool.run(context)

    assert result.trace_id == test_trace_id


def test_dummy_tool_name_is_correct():
    """Test that tool_name is correctly set in result."""
    tool = DummyTool()
    context = ToolContext(
        trace_id="trace-dummy-003",
        agent_id="agent-test",
        params={"test": "data"},
    )

    result = tool.run(context)

    assert result.tool_name == "dummy.echo"
    assert result.tool_name == tool.name


def test_dummy_tool_result_is_json_serializable():
    """Test that result can be serialized to JSON."""
    tool = DummyTool()
    context = ToolContext(
        trace_id="trace-dummy-004",
        agent_id="agent-test",
        params={"test_key": "test_value", "number": 123},
    )

    result = tool.run(context)

    # Use Pydantic's model_dump to convert to dict
    result_dict = result.model_dump()

    # Ensure it's JSON-serializable
    json_str = json.dumps(result_dict)
    assert isinstance(json_str, str)

    # Verify the JSON can be parsed back
    parsed = json.loads(json_str)
    assert parsed["ok"] is True
    assert parsed["trace_id"] == "trace-dummy-004"
    assert parsed["tool_name"] == "dummy.echo"


def test_dummy_tool_error_result_is_json_serializable():
    """Test that error result can be serialized to JSON."""
    tool = DummyTool()
    context = ToolContext(
        trace_id="trace-dummy-005",
        agent_id="agent-test",
        params={},
    )

    result = tool.run(context)

    # Use Pydantic's model_dump to convert to dict
    result_dict = result.model_dump()

    # Ensure it's JSON-serializable
    json_str = json.dumps(result_dict)
    assert isinstance(json_str, str)

    # Verify the JSON can be parsed back
    parsed = json.loads(json_str)
    assert parsed["ok"] is False
    assert parsed["data"] is None
    assert parsed["error"]["code"] == "EMPTY_PARAMS"


def test_dummy_tool_properties():
    """Test that tool properties are correctly defined."""
    tool = DummyTool()

    assert tool.name == "dummy.echo"
    assert tool.description == "Echo back provided params for testing and examples"
    assert tool.version == "v1"
    assert tool.enabled is True


def test_dummy_tool_deterministic():
    """Test that tool produces consistent output for same input."""
    tool = DummyTool()
    params = {"key": "value", "number": 42}

    context1 = ToolContext(
        trace_id="trace-001",
        agent_id="agent-test",
        params=params,
    )
    result1 = tool.run(context1)

    context2 = ToolContext(
        trace_id="trace-001",
        agent_id="agent-test",
        params=params,
    )
    result2 = tool.run(context2)

    # Results should be identical
    assert result1.model_dump() == result2.model_dump()


def test_dummy_tool_with_various_param_types():
    """Test that tool handles various data types in params."""
    tool = DummyTool()
    params = {
        "string": "text",
        "integer": 123,
        "float": 45.67,
        "boolean": True,
        "list": [1, 2, 3],
        "nested_dict": {"inner": "value"},
        "null": None,
    }

    context = ToolContext(
        trace_id="trace-dummy-006",
        agent_id="agent-test",
        params=params,
    )

    result = tool.run(context)

    assert result.ok is True
    assert result.data is not None
    assert result.data["echoed"] == params
