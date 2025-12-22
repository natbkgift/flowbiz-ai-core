"""Tests for tool base interface."""

from __future__ import annotations

import pytest

from packages.core.tools import ToolBase, ToolContext, ToolError, ToolResult


class DummyTool(ToolBase):
    """Dummy tool implementation for testing."""

    @property
    def name(self) -> str:
        return "dummy_tool"

    @property
    def description(self) -> str:
        return "A dummy tool for testing purposes"

    def run(self, context: ToolContext) -> ToolResult:
        """Execute dummy tool logic."""
        # Check for error condition in params
        if context.params.get("should_fail"):
            return ToolResult(
                ok=False,
                data=None,
                error=ToolError(
                    code="DUMMY_ERROR",
                    message="Intentional failure for testing",
                    retryable=True,
                ),
                trace_id=context.trace_id,
                tool_name=self.name,
            )

        # Success path
        result_data = {
            "input_params": context.params,
            "agent_id": context.agent_id,
            "processed": True,
        }
        return ToolResult(
            ok=True,
            data=result_data,
            error=None,
            trace_id=context.trace_id,
            tool_name=self.name,
        )


class CustomVersionTool(ToolBase):
    """Tool with custom version and enabled flag."""

    @property
    def name(self) -> str:
        return "custom_tool"

    @property
    def description(self) -> str:
        return "Tool with custom properties"

    @property
    def version(self) -> str:
        return "v2.1.0"

    @property
    def enabled(self) -> bool:
        return False

    def run(self, context: ToolContext) -> ToolResult:
        """Execute custom tool logic."""
        return ToolResult(
            ok=True,
            data={"version": self.version},
            error=None,
            trace_id=context.trace_id,
            tool_name=self.name,
        )


def test_tool_base_requires_implementation():
    """Test that ToolBase cannot be instantiated directly."""
    with pytest.raises(TypeError):
        ToolBase()  # type: ignore[abstract]


def test_dummy_tool_success():
    """Test successful execution of dummy tool."""
    tool = DummyTool()
    context = ToolContext(
        trace_id="test-trace-123",
        agent_id="test-agent",
        intent="test intent",
        params={"key": "value"},
        metadata={"meta_key": "meta_value"},
    )

    result = tool.run(context)

    assert result.ok is True
    assert result.error is None
    assert result.trace_id == "test-trace-123"
    assert result.tool_name == "dummy_tool"
    assert result.data is not None
    assert result.data["input_params"] == {"key": "value"}
    assert result.data["agent_id"] == "test-agent"
    assert result.data["processed"] is True


def test_dummy_tool_error_path():
    """Test error path of dummy tool."""
    tool = DummyTool()
    context = ToolContext(
        trace_id="test-trace-456",
        agent_id="test-agent",
        params={"should_fail": True},
    )

    result = tool.run(context)

    assert result.ok is False
    assert result.data is None
    assert result.trace_id == "test-trace-456"
    assert result.tool_name == "dummy_tool"
    assert result.error is not None
    assert result.error.code == "DUMMY_ERROR"
    assert result.error.message == "Intentional failure for testing"
    assert result.error.retryable is True


def test_tool_default_properties():
    """Test default version and enabled properties."""
    tool = DummyTool()

    assert tool.name == "dummy_tool"
    assert tool.description == "A dummy tool for testing purposes"
    assert tool.version == "v1"
    assert tool.enabled is True


def test_tool_custom_properties():
    """Test custom version and enabled properties."""
    tool = CustomVersionTool()

    assert tool.name == "custom_tool"
    assert tool.version == "v2.1.0"
    assert tool.enabled is False


def test_tool_context_immutability():
    """Test that ToolContext is immutable."""
    context = ToolContext(
        trace_id="trace-123",
        agent_id="agent-123",
        params={"key": "value"},
    )

    with pytest.raises(Exception):  # Pydantic raises ValidationError or AttributeError
        context.trace_id = "new-trace"  # type: ignore[misc]


def test_tool_result_immutability():
    """Test that ToolResult is immutable."""
    result = ToolResult(
        ok=True,
        data={"result": "success"},
        error=None,
        trace_id="trace-123",
        tool_name="test_tool",
    )

    with pytest.raises(Exception):  # Pydantic raises ValidationError or AttributeError
        result.ok = False  # type: ignore[misc]


def test_tool_error_immutability():
    """Test that ToolError is immutable."""
    error = ToolError(
        code="TEST_ERROR",
        message="Test error message",
        retryable=True,
    )

    with pytest.raises(Exception):  # Pydantic raises ValidationError or AttributeError
        error.code = "NEW_CODE"  # type: ignore[misc]


def test_tool_result_serialization():
    """Test that ToolResult can be serialized to dict."""
    result = ToolResult(
        ok=True,
        data={"key": "value"},
        error=None,
        trace_id="trace-789",
        tool_name="serializable_tool",
    )

    result_dict = result.model_dump()

    assert isinstance(result_dict, dict)
    assert result_dict["ok"] is True
    assert result_dict["data"] == {"key": "value"}
    assert result_dict["error"] is None
    assert result_dict["trace_id"] == "trace-789"
    assert result_dict["tool_name"] == "serializable_tool"


def test_tool_error_serialization():
    """Test that ToolError can be serialized correctly."""
    error = ToolError(
        code="SERIALIZATION_ERROR",
        message="This is a serialization test",
        retryable=False,
    )

    error_dict = error.model_dump()

    assert isinstance(error_dict, dict)
    assert error_dict["code"] == "SERIALIZATION_ERROR"
    assert error_dict["message"] == "This is a serialization test"
    assert error_dict["retryable"] is False


def test_tool_result_with_error_serialization():
    """Test that ToolResult with ToolError serializes correctly."""
    error = ToolError(
        code="NESTED_ERROR",
        message="Nested error message",
        retryable=True,
    )
    result = ToolResult(
        ok=False,
        data=None,
        error=error,
        trace_id="trace-error-123",
        tool_name="error_tool",
    )

    result_dict = result.model_dump()

    assert result_dict["ok"] is False
    assert result_dict["data"] is None
    assert result_dict["error"] is not None
    assert result_dict["error"]["code"] == "NESTED_ERROR"
    assert result_dict["error"]["message"] == "Nested error message"
    assert result_dict["error"]["retryable"] is True


def test_tool_context_default_values():
    """Test that ToolContext uses default values correctly."""
    context = ToolContext(
        trace_id="trace-default",
        agent_id="agent-default",
    )

    assert context.trace_id == "trace-default"
    assert context.agent_id == "agent-default"
    assert context.intent is None
    assert context.params == {}
    assert context.metadata == {}


def test_tool_context_with_all_fields():
    """Test ToolContext with all fields populated."""
    context = ToolContext(
        trace_id="trace-full",
        agent_id="agent-full",
        intent="full test intent",
        params={"param1": "value1", "param2": 123},
        metadata={"meta1": "metavalue1", "meta2": True},
    )

    assert context.trace_id == "trace-full"
    assert context.agent_id == "agent-full"
    assert context.intent == "full test intent"
    assert context.params == {"param1": "value1", "param2": 123}
    assert context.metadata == {"meta1": "metavalue1", "meta2": True}
