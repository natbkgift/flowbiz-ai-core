"""Response contract schemas for agent/tool envelopes and errors."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ResponseError(BaseModel):
    """Normalized error payload for response envelopes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error description")
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional structured metadata for debugging/handling",
    )
    retriable: bool = Field(
        False,
        description="Whether caller may retry safely with same inputs",
    )


class AgentResponseEnvelope(BaseModel):
    """Canonical response envelope for agent execution."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: Literal["ok", "error"]
    trace_id: str
    agent: str
    output: str | None = None
    errors: list[ResponseError] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolResponseEnvelope(BaseModel):
    """Canonical response envelope for tool execution."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: Literal["ok", "error"]
    trace_id: str
    tool: str
    output: dict[str, Any] | None = None
    errors: list[ResponseError] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
