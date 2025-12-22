"""Default stub agent implementation."""

from __future__ import annotations

from .base import AgentBase
from .context import AgentContext
from .result import AgentResult


class DefaultAgent(AgentBase):
    """Minimal deterministic agent that echoes input."""

    def __init__(self):
        super().__init__(name="default")

    def run(self, ctx: AgentContext) -> AgentResult:
        """Return a simple echo response without external dependencies."""

        return AgentResult(
            output_text=f"OK: {ctx.input_text}",
            status="ok",
            reason=None,
            trace={
                "agent_name": self.name,
                "request_id": ctx.request_id,
            },
        )
