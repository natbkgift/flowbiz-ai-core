"""Abstract base class for agents."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .context import AgentContext
from .result import AgentResult


class AgentBase(ABC):
    """Abstract base class for all agents."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, ctx: AgentContext) -> AgentResult:
        """Execute the agent logic and return a result."""
        ...
