"""Observability contract schemas for trace and tool-call logging hooks."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class TraceContextContract(BaseModel):
    """Schema-only trace context contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    trace_id: str
    request_id: str | None = None
    span_id: str | None = None
    parent_span_id: str | None = None


class ToolCallLogEntry(BaseModel):
    """Schema-only tool-call logging entry contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    trace_id: str
    tool_name: str
    status: Literal["ok", "error"]
    started_at: str
    finished_at: str
    duration_ms: int = Field(..., ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    error_code: str | None = None
