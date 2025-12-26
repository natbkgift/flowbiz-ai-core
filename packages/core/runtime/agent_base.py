"""Base agent interface for runtime."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .context import RuntimeContext
from .result import RuntimeResult


class AgentBase(ABC):
    """Abstract base class for runtime agents."""

    def __init__(self, name: str):
        """Initialize agent with a name.

        Args:
            name: Unique identifier for this agent
        """
        self.name = name

    @abstractmethod
    def execute(self, ctx: RuntimeContext) -> RuntimeResult:
        """Execute agent logic and return result.

        Args:
            ctx: Runtime context with input and metadata

        Returns:
            RuntimeResult with status and output
        """
        ...
