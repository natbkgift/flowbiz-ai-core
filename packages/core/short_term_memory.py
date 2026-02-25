"""Short-term memory contract and in-memory store.

Provides a simple key-value memory scoped to a session/run,
suitable for passing data between pipeline steps.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MemoryEntry(BaseModel):
    """A single memory entry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    key: str = Field(..., description="Memory slot key")
    value: Any = Field(..., description="Stored value")


class MemorySnapshot(BaseModel):
    """Snapshot of all memory entries."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    entries: list[MemoryEntry] = Field(default_factory=list, description="All entries")


class ShortTermMemory:
    """In-memory key/value store for a single session."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """Store or overwrite a value."""
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value or *default*."""
        return self._data.get(key, default)

    def delete(self, key: str) -> bool:
        """Remove a key. Returns True if existed."""
        if key in self._data:
            del self._data[key]
            return True
        return False

    def keys(self) -> list[str]:
        """Return sorted list of keys."""
        return sorted(self._data.keys())

    def snapshot(self) -> MemorySnapshot:
        """Return an immutable snapshot."""
        return MemorySnapshot(
            entries=[MemoryEntry(key=k, value=v) for k, v in sorted(self._data.items())]
        )

    def clear(self) -> None:
        """Wipe all entries."""
        self._data.clear()
