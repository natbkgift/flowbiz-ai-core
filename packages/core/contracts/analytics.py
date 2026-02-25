"""Slow query / request tracking contracts — PR-055.

Defines contracts for tracking slow operations and request-level
analytics (PR-056).  Ships with an in-memory store; production
backends (Elasticsearch, ClickHouse, etc.) live outside core.
"""

from __future__ import annotations

import time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# PR-055 — Slow query tracking
# ---------------------------------------------------------------------------


class SlowQueryEntry(BaseModel):
    """Record of a slow operation exceeding a configured threshold."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    operation: str
    duration_ms: float
    threshold_ms: float
    trace_id: str = ""
    timestamp: float = Field(default_factory=time.time)
    metadata: dict[str, str] = Field(default_factory=dict)


class SlowQuerySnapshot(BaseModel):
    """Point-in-time dump of recorded slow queries."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    entries: tuple[SlowQueryEntry, ...] = ()
    threshold_ms: float = 500.0
    collected_at: float = Field(default_factory=time.time)


class InMemorySlowQueryTracker:
    """Records operations that exceed a configurable duration threshold."""

    def __init__(self, threshold_ms: float = 500.0) -> None:
        self._threshold_ms = threshold_ms
        self._entries: list[SlowQueryEntry] = []

    @property
    def threshold_ms(self) -> float:
        return self._threshold_ms

    def record(
        self, operation: str, duration_ms: float, **kwargs: str
    ) -> SlowQueryEntry | None:
        """Record if duration exceeds threshold. Returns entry or None."""
        if duration_ms < self._threshold_ms:
            return None
        entry = SlowQueryEntry(
            operation=operation,
            duration_ms=duration_ms,
            threshold_ms=self._threshold_ms,
            **kwargs,
        )
        self._entries.append(entry)
        return entry

    def snapshot(self) -> SlowQuerySnapshot:
        return SlowQuerySnapshot(
            entries=tuple(self._entries),
            threshold_ms=self._threshold_ms,
        )

    def entries(self) -> list[SlowQueryEntry]:
        return list(self._entries)

    def clear(self) -> None:
        self._entries.clear()


# ---------------------------------------------------------------------------
# PR-056 — Request analytics
# ---------------------------------------------------------------------------

RequestMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]


class RequestLogEntry(BaseModel):
    """Single HTTP request log for analytics purposes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    method: RequestMethod
    path: str
    status_code: int
    duration_ms: float
    trace_id: str = ""
    timestamp: float = Field(default_factory=time.time)
    metadata: dict[str, str] = Field(default_factory=dict)


class RequestAnalyticsSnapshot(BaseModel):
    """Aggregated request analytics."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    total_requests: int = 0
    error_count: int = 0
    avg_duration_ms: float = 0.0
    p95_duration_ms: float = 0.0
    requests_by_path: dict[str, int] = Field(default_factory=dict)
    collected_at: float = Field(default_factory=time.time)


class InMemoryRequestAnalytics:
    """Tracks HTTP request metrics in-memory."""

    def __init__(self) -> None:
        self._entries: list[RequestLogEntry] = []

    def record(self, entry: RequestLogEntry) -> None:
        self._entries.append(entry)

    def snapshot(self) -> RequestAnalyticsSnapshot:
        if not self._entries:
            return RequestAnalyticsSnapshot()
        durations = sorted(e.duration_ms for e in self._entries)
        error_count = sum(1 for e in self._entries if e.status_code >= 400)
        avg_dur = sum(durations) / len(durations)
        p95_idx = int(len(durations) * 0.95)
        p95_dur = durations[min(p95_idx, len(durations) - 1)]
        path_counts: dict[str, int] = {}
        for e in self._entries:
            path_counts[e.path] = path_counts.get(e.path, 0) + 1
        return RequestAnalyticsSnapshot(
            total_requests=len(self._entries),
            error_count=error_count,
            avg_duration_ms=round(avg_dur, 2),
            p95_duration_ms=round(p95_dur, 2),
            requests_by_path=path_counts,
        )

    def entries(self) -> list[RequestLogEntry]:
        return list(self._entries)

    def clear(self) -> None:
        self._entries.clear()
