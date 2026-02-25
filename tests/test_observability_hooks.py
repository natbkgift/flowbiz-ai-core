"""Tests for PR-027 observability hooks."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from packages.core.contracts.observability import ToolCallLogEntry, TraceContextContract
from packages.core.observability import build_tool_call_log_entry, build_trace_context


def test_trace_context_contract_and_immutability() -> None:
    ctx = build_trace_context(
        trace_id="trace-123",
        request_id="req-1",
        span_id="span-a",
        parent_span_id="span-root",
    )

    assert isinstance(ctx, TraceContextContract)
    assert ctx.trace_id == "trace-123"

    with pytest.raises((ValidationError, AttributeError)):
        ctx.trace_id = "changed"  # type: ignore[misc]


def test_build_tool_call_log_entry_ok_path() -> None:
    started_at = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    finished_at = started_at + timedelta(milliseconds=250)

    entry = build_tool_call_log_entry(
        trace_id="trace-1",
        tool_name="dummy",
        status="ok",
        started_at=started_at,
        finished_at=finished_at,
        metadata={"k": "v"},
    )

    assert isinstance(entry, ToolCallLogEntry)
    assert entry.status == "ok"
    assert entry.duration_ms == 250
    assert entry.metadata == {"k": "v"}


def test_build_tool_call_log_entry_clamps_negative_duration() -> None:
    finished_at = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    started_at = finished_at + timedelta(seconds=1)

    entry = build_tool_call_log_entry(
        trace_id="trace-2",
        tool_name="dummy",
        status="error",
        started_at=started_at,
        finished_at=finished_at,
        error_code="TIMEOUT",
    )

    assert entry.duration_ms == 0
    assert entry.error_code == "TIMEOUT"


def test_tool_call_log_entry_rejects_invalid_status() -> None:
    with pytest.raises(ValidationError):
        ToolCallLogEntry(  # type: ignore[call-arg]
            trace_id="trace-3",
            tool_name="dummy",
            status="invalid",
            started_at="2026-01-01T00:00:00+00:00",
            finished_at="2026-01-01T00:00:01+00:00",
            duration_ms=1000,
        )
