"""Observability hook helpers for trace-aware tool-call logging."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .contracts.observability import ToolCallLogEntry, TraceContextContract


def build_trace_context(
    trace_id: str,
    request_id: str | None = None,
    span_id: str | None = None,
    parent_span_id: str | None = None,
) -> TraceContextContract:
    """Build a normalized trace context contract."""
    return TraceContextContract(
        trace_id=trace_id,
        request_id=request_id,
        span_id=span_id,
        parent_span_id=parent_span_id,
    )


def build_tool_call_log_entry(
    *,
    trace_id: str,
    tool_name: str,
    status: str,
    started_at: datetime,
    finished_at: datetime,
    metadata: dict[str, Any] | None = None,
    error_code: str | None = None,
) -> ToolCallLogEntry:
    """Build a deterministic tool-call log entry contract."""
    duration_ms = int((finished_at - started_at).total_seconds() * 1000)
    safe_duration_ms = max(duration_ms, 0)

    return ToolCallLogEntry(
        trace_id=trace_id,
        tool_name=tool_name,
        status=status,  # validated by ToolCallLogEntry
        started_at=started_at.isoformat(),
        finished_at=finished_at.isoformat(),
        duration_ms=safe_duration_ms,
        metadata=metadata or {},
        error_code=error_code,
    )
