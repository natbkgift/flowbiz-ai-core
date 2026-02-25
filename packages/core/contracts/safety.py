"""Safety gate hook contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SafetyDecision(BaseModel):
    """Decision result for safety pre-check."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    decision: Literal["allow", "deny"]
    reason: str | None = None
    code: str | None = None


class SafetyGateInput(BaseModel):
    """Input payload passed to safety gate implementations."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    trace_id: str
    agent: str
    text: str = Field(..., description="User input text for pre-check")
