"""Deterministic vs non-deterministic execution toggle.

Provides a simple runtime flag that controls whether agent execution
should use deterministic (reproducible) or non-deterministic (creative)
mode.  This is an optional contract — agents may ignore it.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ExecutionMode(BaseModel):
    """Runtime execution mode configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    deterministic: bool = Field(
        True,
        description="If True, prefer reproducible outputs (temperature=0, fixed seeds)",
    )
    seed: int | None = Field(
        None, description="Optional random seed for reproducibility"
    )
    temperature: float = Field(
        0.0, description="LLM temperature hint (0.0 = deterministic)"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Extra mode-specific settings"
    )


# Pre-built mode constants
DETERMINISTIC_MODE = ExecutionMode(deterministic=True, temperature=0.0, seed=42)
"""Fully deterministic: temperature=0, seed=42."""

CREATIVE_MODE = ExecutionMode(deterministic=False, temperature=0.7)
"""Non-deterministic: higher temperature, no seed."""


def resolve_mode(
    override: ExecutionMode | None = None,
    default_deterministic: bool = True,
) -> ExecutionMode:
    """Resolve the execution mode, preferring *override* if given."""
    if override is not None:
        return override
    if default_deterministic:
        return DETERMINISTIC_MODE
    return CREATIVE_MODE
