"""Permission model schema and types for tools and agent personas.

This module defines the permission model contracts for FlowBiz AI Core.
These are schema/type definitions only - NO RUNTIME ENFORCEMENT is implemented here.

The types defined here serve as contracts for:
- PR-024: Tool Registry v2 (reads permissions metadata)
- PR-030: Execution Pipeline (calls authorization hook)

Design principles:
- Deny by default
- Least privilege
- Tool declares what it needs
- Agent persona decides what is allowed
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["Permission", "ToolPermissions", "AgentPolicy", "PolicyDecision"]


class Permission(str, Enum):
    """Permission types that tools can require and personas can grant.

    This enum defines the initial set of capabilities in the system.
    Permissions represent access to resources or operations.

    Attributes:
        READ_FS: Read access to filesystem (files, directories)
        WRITE_FS: Write access to filesystem (create, modify, delete)
        NET_HTTP: HTTP/HTTPS network access for external requests
        EXEC_SHELL: Shell command execution on host system
        READ_ENV: Read access to environment variables
        DB_READ: Read access to databases (SELECT queries)
        DB_WRITE: Write access to databases (INSERT, UPDATE, DELETE)
    """

    READ_FS = "READ_FS"
    WRITE_FS = "WRITE_FS"
    NET_HTTP = "NET_HTTP"
    EXEC_SHELL = "EXEC_SHELL"
    READ_ENV = "READ_ENV"
    DB_READ = "DB_READ"
    DB_WRITE = "DB_WRITE"


class ToolPermissions(BaseModel):
    """Permission requirements declared by a tool.

    Tools declare what permissions they need through this schema.
    This metadata is read by the Tool Registry and used by the
    authorization system (future: PR-030).

    Attributes:
        required_permissions: Permissions the tool MUST have to execute.
            If any required permission is denied, tool execution is blocked.
        optional_permissions: Permissions the tool CAN use if available.
            Tool can function without these but may have reduced capabilities.

    Example:
        >>> perms = ToolPermissions(
        ...     required_permissions=[Permission.READ_FS, Permission.NET_HTTP],
        ...     optional_permissions=[Permission.WRITE_FS]
        ... )
        >>> # Tool requires filesystem read + network, optionally writes files
    """

    required_permissions: list[Permission] = Field(
        default_factory=list,
        description="Permissions required for tool execution",
    )
    optional_permissions: list[Permission] = Field(
        default_factory=list,
        description="Permissions that enhance tool capabilities if granted",
    )

    model_config = ConfigDict(frozen=True)


class AgentPolicy(BaseModel):
    """Permission policy for an agent persona.

    Defines what permissions an agent with a given persona is allowed to use.
    This is the authorization boundary for the agent.

    Attributes:
        persona: Agent category/role (e.g., "core", "infra", "docs")
        allowed_permissions: Permissions this persona can grant to tools.
            Tools requesting permissions outside this set will be denied.
        allowed_tools: Optional allowlist of specific tool names.
            If non-empty, only these tools can execute (even if permissions match).
            If empty, all tools are allowed (subject to permission checks).

    Example:
        >>> policy = AgentPolicy(
        ...     persona="core",
        ...     allowed_permissions=[Permission.NET_HTTP, Permission.READ_ENV],
        ...     allowed_tools=["web_search", "fetch_api"]
        ... )
        >>> # Core agents can use NET_HTTP and READ_ENV, but only these two tools
    """

    persona: str = Field(
        description="Agent persona identifier (e.g., 'core', 'infra', 'docs')"
    )
    allowed_permissions: list[Permission] = Field(
        default_factory=list,
        description="Permissions this persona is authorized to use",
    )
    allowed_tools: list[str] = Field(
        default_factory=list,
        description="Optional allowlist of tool names (empty = all tools allowed)",
    )

    model_config = ConfigDict(frozen=True)


class PolicyDecision(BaseModel):
    """Result of an authorization check.

    Returned by the authorization function (future: PR-030) to indicate
    whether a tool execution is allowed or denied.

    Attributes:
        allowed: True if tool can execute, False if denied
        reason: Human-readable explanation of the decision.
            For denials, explains why (e.g., "Missing required permission: EXEC_SHELL")
            For approvals, may be empty or "All checks passed"

    Example:
        >>> decision = PolicyDecision(
        ...     allowed=False,
        ...     reason="Missing required permissions: EXEC_SHELL, WRITE_FS"
        ... )
        >>> if not decision.allowed:
        ...     print(f"Denied: {decision.reason}")
    """

    allowed: bool = Field(description="Whether tool execution is authorized")
    reason: str = Field(
        default="",
        description="Explanation of authorization decision",
    )

    model_config = ConfigDict(frozen=True)
