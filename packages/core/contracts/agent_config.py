"""Agent configuration contract schemas.

Defines immutable schemas for agent configuration that can be loaded
from YAML files, dictionaries, or environment-based sources.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .persona import PersonaType


class AgentConfig(BaseModel):
    """Configuration block for a single agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_name: str = Field(..., description="Unique agent identifier")
    persona: PersonaType = Field(..., description="Persona this agent serves")
    description: str = Field("", description="Human-readable description")
    enabled: bool = Field(True, description="Whether the agent is active")
    tags: list[str] = Field(default_factory=list, description="Categorisation tags")
    allowed_tools: list[str] = Field(
        default_factory=list,
        description="Tool allowlist (empty = all tools allowed)",
    )


class AgentConfigSet(BaseModel):
    """A collection of agent configurations."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agents: list[AgentConfig] = Field(
        default_factory=list, description="Agent configuration entries"
    )
