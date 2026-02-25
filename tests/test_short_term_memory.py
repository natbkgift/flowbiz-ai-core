"""Tests for short-term memory."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.short_term_memory import MemoryEntry, MemorySnapshot, ShortTermMemory


class TestMemoryContracts:
    def test_entry_frozen(self) -> None:
        e = MemoryEntry(key="k", value="v")
        with pytest.raises(ValidationError):
            e.key = "x"  # type: ignore[misc]

    def test_snapshot_frozen(self) -> None:
        s = MemorySnapshot()
        with pytest.raises(ValidationError):
            s.entries = []  # type: ignore[misc]


class TestShortTermMemory:
    def test_set_and_get(self) -> None:
        m = ShortTermMemory()
        m.set("a", 1)
        assert m.get("a") == 1

    def test_get_default(self) -> None:
        m = ShortTermMemory()
        assert m.get("missing", 42) == 42

    def test_overwrite(self) -> None:
        m = ShortTermMemory()
        m.set("a", 1)
        m.set("a", 2)
        assert m.get("a") == 2

    def test_delete(self) -> None:
        m = ShortTermMemory()
        m.set("a", 1)
        assert m.delete("a") is True
        assert m.get("a") is None

    def test_delete_missing(self) -> None:
        m = ShortTermMemory()
        assert m.delete("x") is False

    def test_keys_sorted(self) -> None:
        m = ShortTermMemory()
        m.set("z", 1)
        m.set("a", 2)
        assert m.keys() == ["a", "z"]

    def test_snapshot(self) -> None:
        m = ShortTermMemory()
        m.set("b", 2)
        m.set("a", 1)
        snap = m.snapshot()
        assert len(snap.entries) == 2
        assert snap.entries[0].key == "a"

    def test_clear(self) -> None:
        m = ShortTermMemory()
        m.set("a", 1)
        m.clear()
        assert m.keys() == []
