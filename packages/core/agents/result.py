"""Agent execution result schema."""

from __future__ import annotations

from typing import Any, Literal

from packages.core.schemas.base import BaseSchema


class AgentResult(BaseSchema):
    """Result of agent execution with strict schema validation."""

    output_text: str
    status: Literal["ok", "refused", "error"]
    reason: str | None = None
    trace: dict[str, Any] = {}
