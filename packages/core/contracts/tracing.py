"""Tracing / OpenTelemetry contracts — PR-053.

Defines span and trace contracts compatible with the OpenTelemetry
data model.  Core only defines the contracts; actual OTel SDK
integration lives in platform code.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

SpanStatus = Literal["ok", "error", "unset"]


def _new_id() -> str:
    return uuid.uuid4().hex


class SpanContext(BaseModel):
    """Immutable span context (W3C trace-context compatible)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    trace_id: str = Field(default_factory=_new_id)
    span_id: str = Field(default_factory=_new_id)
    parent_span_id: str | None = None


class SpanEvent(BaseModel):
    """Annotation / log recorded within a span."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    timestamp: float = Field(default_factory=time.time)
    attributes: dict[str, Any] = Field(default_factory=dict)


class Span(BaseModel):
    """Core span contract — mirrors OTel Span."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    context: SpanContext = Field(default_factory=SpanContext)
    name: str = ""
    status: SpanStatus = "unset"
    start_time: float = Field(default_factory=time.time)
    end_time: float | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    events: tuple[SpanEvent, ...] = ()


class TraceExport(BaseModel):
    """Batch of spans for export."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    spans: tuple[Span, ...] = ()
    resource_attributes: dict[str, str] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# In-memory span collector (stub)
# ---------------------------------------------------------------------------


class InMemorySpanCollector:
    """Collects spans in-memory for testing / local dev."""

    def __init__(self) -> None:
        self._spans: list[Span] = []

    def record(self, span: Span) -> None:
        self._spans.append(span)

    def spans(self) -> list[Span]:
        return list(self._spans)

    def export(self) -> TraceExport:
        return TraceExport(spans=tuple(self._spans))

    def find_by_trace(self, trace_id: str) -> list[Span]:
        return [s for s in self._spans if s.context.trace_id == trace_id]

    def clear(self) -> None:
        self._spans.clear()
