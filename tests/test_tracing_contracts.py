"""Tests for tracing contracts — PR-053."""

from __future__ import annotations

from packages.core.contracts.tracing import (
    InMemorySpanCollector,
    Span,
    SpanContext,
    SpanEvent,
    TraceExport,
)


class TestSpanContext:
    def test_auto_ids(self) -> None:
        ctx = SpanContext()
        assert len(ctx.trace_id) == 32
        assert len(ctx.span_id) == 32
        assert ctx.parent_span_id is None

    def test_with_parent(self) -> None:
        ctx = SpanContext(parent_span_id="abc123")
        assert ctx.parent_span_id == "abc123"


class TestSpanEvent:
    def test_schema(self) -> None:
        ev = SpanEvent(name="log", attributes={"key": "val"})
        assert ev.name == "log"
        assert ev.attributes["key"] == "val"
        assert ev.timestamp > 0


class TestSpan:
    def test_defaults(self) -> None:
        s = Span(name="test-op")
        assert s.name == "test-op"
        assert s.status == "unset"
        assert s.end_time is None
        assert s.events == ()

    def test_with_events(self) -> None:
        ev = SpanEvent(name="checkpoint")
        s = Span(name="op", events=(ev,))
        assert len(s.events) == 1

    def test_status_values(self) -> None:
        for st in ("ok", "error", "unset"):
            s = Span(name="op", status=st)  # type: ignore[arg-type]
            assert s.status == st


class TestTraceExport:
    def test_empty(self) -> None:
        te = TraceExport()
        assert te.spans == ()
        assert te.resource_attributes == {}


class TestInMemorySpanCollector:
    def test_record_and_list(self) -> None:
        c = InMemorySpanCollector()
        s = Span(name="op1")
        c.record(s)
        assert len(c.spans()) == 1

    def test_export(self) -> None:
        c = InMemorySpanCollector()
        c.record(Span(name="a"))
        c.record(Span(name="b"))
        export = c.export()
        assert len(export.spans) == 2

    def test_find_by_trace(self) -> None:
        c = InMemorySpanCollector()
        ctx = SpanContext(trace_id="aaa")
        c.record(Span(name="op1", context=ctx))
        c.record(Span(name="op2"))
        found = c.find_by_trace("aaa")
        assert len(found) == 1
        assert found[0].name == "op1"

    def test_clear(self) -> None:
        c = InMemorySpanCollector()
        c.record(Span(name="x"))
        c.clear()
        assert c.spans() == []
