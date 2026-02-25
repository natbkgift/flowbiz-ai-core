"""Routing rule contract schemas.

Defines immutable schemas for rule-based intent routing: matching
an inbound intent string to a target agent/persona via keyword or
pattern rules, evaluated in priority order.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .persona import PersonaType

MatchStrategy = Literal["keyword", "pattern"]
"""How the rule matches against the intent string."""


class RoutingRule(BaseModel):
    """A single routing rule evaluated by the intent router."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rule_id: str = Field(..., description="Unique rule identifier")
    match_strategy: MatchStrategy = Field(
        ..., description="How to match (keyword = substring, pattern = regex)"
    )
    match_value: str = Field(
        ...,
        description="Value to match: a keyword substring or regex pattern",
    )
    target_persona: PersonaType = Field(
        ..., description="Persona the intent should be routed to"
    )
    target_agent: str | None = Field(
        None,
        description="Optional specific agent within the persona",
    )
    priority: int = Field(
        0,
        description="Higher value = higher priority; ties break by insertion order",
    )
    enabled: bool = Field(True, description="Whether this rule is active")


class RoutingResult(BaseModel):
    """Outcome of routing an intent string through the rule engine."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    matched: bool = Field(..., description="Whether any rule matched")
    rule_id: str | None = Field(
        None, description="ID of the rule that matched (if any)"
    )
    target_persona: PersonaType | None = Field(
        None, description="Resolved target persona"
    )
    target_agent: str | None = Field(
        None, description="Resolved target agent (if specified by rule)"
    )
