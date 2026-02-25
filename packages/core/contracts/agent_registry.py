"""Agent Registry v2 contract schemas.

This module defines immutable, schema-only contracts for Agent Registry v2.
"""

from pydantic import BaseModel, ConfigDict, Field


class AgentSpec(BaseModel):
    """Agent specification schema."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_name: str = Field(..., description="Unique identifier for the agent")
    version: str | None = Field(None, description="Agent version identifier")
    description: str | None = Field(
        None, description="Human-readable description of the agent"
    )
    tags: list[str] = Field(
        default_factory=list, description="List of tags for categorization"
    )


class AgentRegistration(BaseModel):
    """Agent registration record in the registry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    spec: AgentSpec = Field(..., description="The agent specification")
    enabled: bool = Field(True, description="Whether the agent is enabled")
    created_at: str | None = Field(
        None, description="ISO8601 timestamp of when the agent was registered"
    )


class AgentRegistrySnapshot(BaseModel):
    """Snapshot of Agent Registry state."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agents: list[AgentRegistration] = Field(..., description="Registered agents")
