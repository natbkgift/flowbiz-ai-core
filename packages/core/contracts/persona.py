"""Persona contract schemas.

Defines the three core personas (core, infra, docs) as first-class
schema objects so agents can declare which persona they serve.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PersonaType = Literal["core", "infra", "docs"]
"""Allowed persona identifiers — mirrors the project persona labels."""


class PersonaSpec(BaseModel):
    """Specification for a persona."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    persona: PersonaType = Field(..., description="Persona identifier")
    display_name: str = Field(..., description="Human-friendly label")
    description: str = Field("", description="What this persona is responsible for")


class PersonaAssignment(BaseModel):
    """Links an agent name to a persona."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_name: str = Field(..., description="Agent identifier")
    persona: PersonaType = Field(..., description="Assigned persona")


# Pre-built specs for the three canonical personas.
CORE_PERSONA = PersonaSpec(
    persona="core",
    display_name="Core",
    description="Core domain logic, runtime primitives, and contracts.",
)

INFRA_PERSONA = PersonaSpec(
    persona="infra",
    display_name="Infra",
    description="Infrastructure, deployment, and operational tasks.",
)

DOCS_PERSONA = PersonaSpec(
    persona="docs",
    display_name="Docs",
    description="Documentation updates and knowledge-base tasks.",
)

ALL_PERSONAS: dict[PersonaType, PersonaSpec] = {
    "core": CORE_PERSONA,
    "infra": INFRA_PERSONA,
    "docs": DOCS_PERSONA,
}
