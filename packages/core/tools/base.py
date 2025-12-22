"""Abstract base class for tool implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .context import ToolContext
from .result import ToolResult


class ToolBase(ABC):
    """Abstract base class for all tools.

    Tools must implement this interface to be used by agents.
    This class enforces a consistent contract without introducing
    side effects or execution logic.

    Attributes:
        name: Unique identifier for the tool
        description: Human-readable description of what the tool does
        version: Tool version identifier (default: "v1")
        enabled: Whether the tool is currently enabled (default: True)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique name of this tool."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what this tool does."""
        ...

    @property
    def version(self) -> str:
        """Return the version of this tool.

        Returns:
            Tool version identifier (default: "v1")
        """
        return "v1"

    @property
    def enabled(self) -> bool:
        """Return whether this tool is enabled.

        Returns:
            True if the tool is enabled, False otherwise (default: True)
        """
        return True

    @abstractmethod
    def run(self, context: ToolContext) -> ToolResult:
        """Execute the tool with the given context.

        Args:
            context: Execution context containing input parameters and metadata

        Returns:
            Structured result containing output data or error information
        """
        ...
