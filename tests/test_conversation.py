"""Tests for conversation state contracts and manager."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.conversation import (
    ConversationManager,
    ConversationState,
    ConversationTurn,
)


class TestConversationContracts:
    def test_turn_frozen(self) -> None:
        t = ConversationTurn(role="user", content="hello")
        with pytest.raises(ValidationError):
            t.role = "agent"  # type: ignore[misc]

    def test_turn_rejects_invalid_role(self) -> None:
        with pytest.raises(ValidationError):
            ConversationTurn(role="bot", content="x")  # type: ignore[arg-type]

    def test_state_frozen(self) -> None:
        s = ConversationState(conversation_id="c1")
        with pytest.raises(ValidationError):
            s.conversation_id = "c2"  # type: ignore[misc]


class TestConversationManager:
    def test_add_turn(self) -> None:
        mgr = ConversationManager("c1")
        t = mgr.add_turn("user", "hello")
        assert t.role == "user"
        assert t.content == "hello"
        assert mgr.turn_count == 1

    def test_snapshot(self) -> None:
        mgr = ConversationManager("c1")
        mgr.add_turn("user", "hi")
        mgr.add_turn("agent", "hello")
        snap = mgr.snapshot()
        assert snap.conversation_id == "c1"
        assert len(snap.turns) == 2

    def test_metadata(self) -> None:
        mgr = ConversationManager("c1")
        t = mgr.add_turn("user", "x", source="web")
        assert t.metadata == {"source": "web"}

    def test_clear(self) -> None:
        mgr = ConversationManager("c1")
        mgr.add_turn("user", "x")
        mgr.clear()
        assert mgr.turn_count == 0

    def test_multiple_snapshots_independent(self) -> None:
        mgr = ConversationManager("c1")
        mgr.add_turn("user", "a")
        snap1 = mgr.snapshot()
        mgr.add_turn("agent", "b")
        snap2 = mgr.snapshot()
        assert len(snap1.turns) == 1
        assert len(snap2.turns) == 2
