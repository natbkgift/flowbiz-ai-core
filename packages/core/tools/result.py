"""Tool result and error definitions for structured tool outputs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class ToolError(BaseModel):
    """Error information for failed tool execution.

    Attributes:
        code: Error code identifying the type of error
        message: Human-readable error message
        retryable: Whether the operation can be retried
    """

    code: str
    message: str
    retryable: bool = False

    model_config = ConfigDict(frozen=True)


class ToolResult(BaseModel):
    """Structured result from tool execution.

    Attributes:
        ok: Whether the tool execution succeeded
        data: Output data from successful execution
        error: Error information if execution failed
        trace_id: Trace identifier for observability
        tool_name: Name of the tool that produced this result
    """

    ok: bool
    data: dict[str, Any] | None = None
    error: ToolError | None = None
    trace_id: str
    tool_name: str

    model_config = ConfigDict(frozen=True)
