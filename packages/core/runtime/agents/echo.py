"""Echo agent for runtime testing."""

from __future__ import annotations

from ..agent_base import AgentBase
from ..context import RuntimeContext
from ..result import RuntimeResult


class EchoAgent(AgentBase):
    """Deterministic echo agent that returns input as output."""

    def __init__(self):
        """Initialize echo agent."""
        super().__init__(name="echo")

    def execute(self, ctx: RuntimeContext) -> RuntimeResult:
        """Echo the input back as output.

        Args:
            ctx: Runtime context with input

        Returns:
            RuntimeResult with status=ok and output=input
        """
        return RuntimeResult(
            status="ok",
            trace_id=ctx.trace_id,
            agent=self.name,
            output=ctx.input,
            errors=[],
        )
