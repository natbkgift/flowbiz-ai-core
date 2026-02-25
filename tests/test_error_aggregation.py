"""Tests for error aggregation contracts — PR-054."""

from __future__ import annotations

from packages.core.contracts.errors import (
    ErrorAggregateSnapshot,
    ErrorEntry,
    ErrorGroup,
    InMemoryErrorAggregator,
)


class TestErrorEntry:
    def test_schema(self) -> None:
        e = ErrorEntry(error_type="ValueError", message="bad input")
        assert e.error_type == "ValueError"
        assert e.severity == "medium"
        assert e.timestamp > 0

    def test_severity_values(self) -> None:
        for s in ("low", "medium", "high", "critical"):
            e = ErrorEntry(error_type="X", message="m", severity=s)  # type: ignore[arg-type]
            assert e.severity == s


class TestErrorGroup:
    def test_schema(self) -> None:
        g = ErrorGroup(
            error_type="ValueError",
            count=5,
            severity="high",
            first_seen=1.0,
            last_seen=2.0,
        )
        assert g.count == 5


class TestErrorAggregateSnapshot:
    def test_empty(self) -> None:
        snap = ErrorAggregateSnapshot()
        assert snap.groups == ()
        assert snap.total_errors == 0


class TestInMemoryErrorAggregator:
    def test_record_and_count(self) -> None:
        a = InMemoryErrorAggregator()
        a.record(ErrorEntry(error_type="ValueError", message="bad"))
        a.record(ErrorEntry(error_type="ValueError", message="bad2"))
        a.record(ErrorEntry(error_type="KeyError", message="missing"))
        assert a.count_for("ValueError") == 2
        assert a.count_for("KeyError") == 1

    def test_snapshot(self) -> None:
        a = InMemoryErrorAggregator()
        a.record(ErrorEntry(error_type="A", message="m1"))
        a.record(ErrorEntry(error_type="A", message="m2"))
        a.record(ErrorEntry(error_type="B", message="m3", severity="critical"))
        snap = a.snapshot()
        assert snap.total_errors == 3
        assert len(snap.groups) == 2

    def test_entries(self) -> None:
        a = InMemoryErrorAggregator()
        a.record(ErrorEntry(error_type="X", message="y"))
        assert len(a.entries()) == 1

    def test_clear(self) -> None:
        a = InMemoryErrorAggregator()
        a.record(ErrorEntry(error_type="X", message="y"))
        a.clear()
        assert a.count_for("X") == 0
        assert a.entries() == []
