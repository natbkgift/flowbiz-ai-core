"""Tool context definition for safe tool input."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolContext(BaseModel):
    """Immutable context for tool execution.

    Provides all necessary input and metadata for a tool to execute
    without requiring knowledge of agent internals.

    Attributes:
        trace_id: Trace identifier for observability
        agent_id: Identifier of the agent invoking the tool
        intent: Optional intent description
        params: Input parameters for the tool
        metadata: Additional metadata
    """

    trace_id: str
    agent_id: str
    intent: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(frozen=True)
