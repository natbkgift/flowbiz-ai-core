"""Error aggregation contracts — PR-054.

Defines structured error entries, severity levels, and an in-memory
error aggregator for grouping / counting errors.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ErrorSeverity = Literal["low", "medium", "high", "critical"]


class ErrorEntry(BaseModel):
    """Single error occurrence."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    error_type: str
    message: str
    severity: ErrorSeverity = "medium"
    trace_id: str = ""
    timestamp: float = Field(default_factory=time.time)
    metadata: dict[str, str] = Field(default_factory=dict)


class ErrorGroup(BaseModel):
    """Aggregated group of identical error types."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    error_type: str
    count: int
    severity: ErrorSeverity
    first_seen: float
    last_seen: float
    sample_message: str = ""


class ErrorAggregateSnapshot(BaseModel):
    """Point-in-time snapshot of aggregated errors."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    groups: tuple[ErrorGroup, ...] = ()
    total_errors: int = 0
    collected_at: float = Field(default_factory=time.time)


# ---------------------------------------------------------------------------
# In-memory aggregator
# ---------------------------------------------------------------------------


class InMemoryErrorAggregator:
    """Groups errors by type and tracks counts / timestamps."""

    def __init__(self) -> None:
        self._entries: list[ErrorEntry] = []
        self._counts: dict[str, int] = defaultdict(int)

    def record(self, entry: ErrorEntry) -> None:
        self._entries.append(entry)
        self._counts[entry.error_type] += 1

    def snapshot(self) -> ErrorAggregateSnapshot:
        groups_map: dict[str, list[ErrorEntry]] = defaultdict(list)
        for e in self._entries:
            groups_map[e.error_type].append(e)

        groups: list[ErrorGroup] = []
        for etype, entries in groups_map.items():
            groups.append(
                ErrorGroup(
                    error_type=etype,
                    count=len(entries),
                    severity=entries[-1].severity,
                    first_seen=entries[0].timestamp,
                    last_seen=entries[-1].timestamp,
                    sample_message=entries[0].message,
                )
            )
        return ErrorAggregateSnapshot(
            groups=tuple(groups),
            total_errors=sum(self._counts.values()),
        )

    def count_for(self, error_type: str) -> int:
        return self._counts.get(error_type, 0)

    def entries(self) -> list[ErrorEntry]:
        return list(self._entries)

    def clear(self) -> None:
        self._entries.clear()
        self._counts.clear()
