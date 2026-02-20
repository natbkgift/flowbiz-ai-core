"""Tool Registry v2 contract schemas.

This module defines the schema-only contracts for Tool Registry v2.
All models are frozen and immutable, ensuring deterministic behavior.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolSpec(BaseModel):
    """Tool specification schema.

    Defines the metadata and schema information for a tool.
    This is a pure data contract with no execution logic.

    Attributes:
        tool_name: Unique identifier for the tool (required)
        version: Tool version identifier (optional, e.g., "1.0.0")
        description: Human-readable description of what the tool does (optional)
        input_schema: JSON-serializable schema defining expected inputs
        output_schema: JSON-serializable schema defining expected outputs
        tags: List of tags for categorization and discovery (optional)
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    tool_name: str = Field(..., description="Unique identifier for the tool")
    version: str | None = Field(None, description="Tool version identifier")
    description: str | None = Field(
        None, description="Human-readable description of what the tool does"
    )
    input_schema: dict[str, Any] = Field(
        ..., description="JSON-serializable schema defining expected inputs"
    )
    output_schema: dict[str, Any] = Field(
        ..., description="JSON-serializable schema defining expected outputs"
    )
    tags: list[str] = Field(
        default_factory=list, description="List of tags for categorization"
    )


class ToolRegistration(BaseModel):
    """Tool registration record.

    Represents a registered tool with its specification and runtime state.
    The enabled flag controls whether the tool is available for use.

    Attributes:
        spec: The tool specification
        enabled: Whether the tool is currently enabled (default: True)
        created_at: ISO8601 timestamp of when the tool was registered (optional)
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    spec: ToolSpec = Field(..., description="The tool specification")
    enabled: bool = Field(True, description="Whether the tool is currently enabled")
    created_at: str | None = Field(
        None, description="ISO8601 timestamp of when the tool was registered"
    )


class ToolRegistrySnapshot(BaseModel):
    """Snapshot of the tool registry state.

    Contains a list of all tool registrations at a point in time.
    This is useful for serialization, persistence, and state transfer.

    Attributes:
        tools: List of tool registrations
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    tools: list[ToolRegistration] = Field(..., description="List of tool registrations")
