"""Conversation state contract schemas.

Defines a deterministic, serialisable conversation state that tracks
turns in a conversation between user and agent.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Role = Literal["user", "agent", "system"]
"""Who produced a conversation turn."""


class ConversationTurn(BaseModel):
    """A single turn in the conversation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    role: Role = Field(..., description="Who produced this turn")
    content: str = Field(..., description="Turn text content")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Optional metadata"
    )


class ConversationState(BaseModel):
    """Full conversation state — ordered list of turns."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    conversation_id: str = Field(..., description="Unique conversation identifier")
    turns: list[ConversationTurn] = Field(
        default_factory=list, description="Ordered turns"
    )


class ConversationManager:
    """Mutable manager that builds conversation states."""

    def __init__(self, conversation_id: str) -> None:
        self._id = conversation_id
        self._turns: list[ConversationTurn] = []

    def add_turn(self, role: Role, content: str, **metadata: Any) -> ConversationTurn:
        """Append a turn and return it."""
        turn = ConversationTurn(role=role, content=content, metadata=metadata)
        self._turns.append(turn)
        return turn

    def snapshot(self) -> ConversationState:
        """Return an immutable snapshot of current state."""
        return ConversationState(conversation_id=self._id, turns=list(self._turns))

    @property
    def turn_count(self) -> int:
        return len(self._turns)

    def clear(self) -> None:
        self._turns.clear()
