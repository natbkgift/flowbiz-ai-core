"""Agent runtime orchestrator."""

from __future__ import annotations

from .agent_base import AgentBase
from .agents.echo import EchoAgent
from .context import RuntimeContext
from .result import RuntimeError, RuntimeResult


class AgentRuntime:
    """Orchestrates agent execution with built-in agent registry."""

    def __init__(self):
        """Initialize runtime with built-in agents."""
        self._agents: dict[str, AgentBase] = {
            "echo": EchoAgent(),
        }

    def run(self, ctx: RuntimeContext) -> RuntimeResult:
        """Execute agent specified in context.

        Args:
            ctx: Runtime context with agent name and input

        Returns:
            RuntimeResult with execution outcome
        """
        agent = self._agents.get(ctx.agent)

        if agent is None:
            return RuntimeResult(
                status="error",
                trace_id=ctx.trace_id,
                agent=ctx.agent,
                output=None,
                errors=[
                    RuntimeError(
                        code="AGENT_NOT_FOUND",
                        message=f"Agent '{ctx.agent}' not found",
                        details={"agent": ctx.agent},
                    )
                ],
            )

        try:
            return agent.execute(ctx)
        except Exception as exc:
            return RuntimeResult(
                status="error",
                trace_id=ctx.trace_id,
                agent=ctx.agent,
                output=None,
                errors=[
                    RuntimeError(
                        code="RUNTIME_ERROR",
                        message=str(exc),
                        details={},
                    )
                ],
            )
