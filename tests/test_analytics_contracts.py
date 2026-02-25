"""Tests for slow query tracking and request analytics — PR-055, PR-056."""

from __future__ import annotations

from packages.core.contracts.analytics import (
    InMemoryRequestAnalytics,
    InMemorySlowQueryTracker,
    RequestLogEntry,
    SlowQueryEntry,
)


class TestSlowQueryEntry:
    def test_schema(self) -> None:
        e = SlowQueryEntry(operation="db.query", duration_ms=600.0, threshold_ms=500.0)
        assert e.operation == "db.query"
        assert e.duration_ms == 600.0


class TestInMemorySlowQueryTracker:
    def test_below_threshold_not_recorded(self) -> None:
        t = InMemorySlowQueryTracker(threshold_ms=500.0)
        result = t.record("fast_op", 100.0)
        assert result is None
        assert len(t.entries()) == 0

    def test_above_threshold_recorded(self) -> None:
        t = InMemorySlowQueryTracker(threshold_ms=500.0)
        result = t.record("slow_op", 800.0)
        assert result is not None
        assert result.operation == "slow_op"
        assert len(t.entries()) == 1

    def test_snapshot(self) -> None:
        t = InMemorySlowQueryTracker(threshold_ms=100.0)
        t.record("op1", 200.0)
        t.record("op2", 50.0)
        t.record("op3", 150.0)
        snap = t.snapshot()
        assert len(snap.entries) == 2
        assert snap.threshold_ms == 100.0

    def test_clear(self) -> None:
        t = InMemorySlowQueryTracker(threshold_ms=100.0)
        t.record("op", 200.0)
        t.clear()
        assert t.entries() == []


class TestRequestLogEntry:
    def test_schema(self) -> None:
        e = RequestLogEntry(
            method="GET", path="/api/test", status_code=200, duration_ms=50.0
        )
        assert e.method == "GET"
        assert e.status_code == 200


class TestInMemoryRequestAnalytics:
    def test_empty_snapshot(self) -> None:
        a = InMemoryRequestAnalytics()
        snap = a.snapshot()
        assert snap.total_requests == 0
        assert snap.avg_duration_ms == 0.0

    def test_record_and_snapshot(self) -> None:
        a = InMemoryRequestAnalytics()
        a.record(
            RequestLogEntry(method="GET", path="/a", status_code=200, duration_ms=10.0)
        )
        a.record(
            RequestLogEntry(method="GET", path="/a", status_code=200, duration_ms=20.0)
        )
        a.record(
            RequestLogEntry(
                method="POST", path="/b", status_code=500, duration_ms=100.0
            )
        )
        snap = a.snapshot()
        assert snap.total_requests == 3
        assert snap.error_count == 1
        assert snap.avg_duration_ms > 0
        assert snap.requests_by_path["/a"] == 2
        assert snap.requests_by_path["/b"] == 1

    def test_p95(self) -> None:
        a = InMemoryRequestAnalytics()
        for i in range(100):
            a.record(
                RequestLogEntry(
                    method="GET", path="/x", status_code=200, duration_ms=float(i + 1)
                )
            )
        snap = a.snapshot()
        assert snap.p95_duration_ms >= 95.0

    def test_clear(self) -> None:
        a = InMemoryRequestAnalytics()
        a.record(
            RequestLogEntry(method="GET", path="/x", status_code=200, duration_ms=5.0)
        )
        a.clear()
        assert a.entries() == []
