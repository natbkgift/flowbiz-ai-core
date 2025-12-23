"""Tool base interface for agent tool execution.

This module provides the foundation for creating tools that agents can invoke.
It defines contracts for tool inputs (ToolContext), outputs (ToolResult),
and the base interface (ToolBase) that all tools must implement.
"""

from __future__ import annotations

from .authorize import authorize
from .base import ToolBase
from .context import ToolContext
from .permissions import AgentPolicy, Permission, PolicyDecision, ToolPermissions
from .result import ToolError, ToolResult

__all__ = [
    "AgentPolicy",
    "Permission",
    "PolicyDecision",
    "ToolPermissions",
    "ToolBase",
    "ToolContext",
    "ToolError",
    "ToolResult",
    "authorize",
]
