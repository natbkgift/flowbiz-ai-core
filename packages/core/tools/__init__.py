"""Tool base interface for agent tool execution.

This module provides the foundation for creating tools that agents can invoke.
It defines contracts for tool inputs (ToolContext), outputs (ToolResult),
and the base interface (ToolBase) that all tools must implement.
"""

from __future__ import annotations

from .base import ToolBase
from .context import ToolContext
from .result import ToolError, ToolResult

__all__ = ["ToolBase", "ToolContext", "ToolError", "ToolResult"]
