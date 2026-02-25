"""Agent runtime orchestrator."""

from __future__ import annotations

from ..agent_registry import InMemoryAgentRegistry
from ..contracts.agent_registry import AgentSpec
from .agent_base import AgentBase
from .agents.echo import EchoAgent
from .context import RuntimeContext
from .result import RuntimeError, RuntimeResult


class AgentRuntime:
    """Orchestrates agent execution with built-in agent registry."""

    def __init__(self):
        """Initialize runtime with built-in agents."""
        self._agents: dict[str, AgentBase] = {}
        self._registry = InMemoryAgentRegistry()
        self.register_agent(EchoAgent())

    def _ensure_registry_entry(self, agent: AgentBase) -> None:
        """Ensure agent has a registry entry.

        This keeps backward compatibility for direct test-time map mutation while
        converging runtime behavior around registry checks.
        """
        if self._registry.get(agent.name) is not None:
            return

        self._registry.register(
            AgentSpec(agent_name=agent.name, description=agent.__class__.__name__)
        )

    def register_agent(self, agent: AgentBase) -> None:
        """Register an agent in the runtime registry."""
        self._agents[agent.name] = agent
        self._registry.register(
            AgentSpec(agent_name=agent.name, description=agent.__class__.__name__)
        )

    def set_agent_enabled(self, agent_name: str, enabled: bool) -> None:
        """Enable or disable an agent in the runtime registry."""
        agent = self._agents.get(agent_name)
        if agent is not None:
            self._ensure_registry_entry(agent)
        self._registry.set_enabled(agent_name, enabled)

    def enable_agent(self, agent_name: str) -> None:
        """Enable an agent in the runtime registry."""
        self.set_agent_enabled(agent_name, enabled=True)

    def disable_agent(self, agent_name: str) -> None:
        """Disable an agent in the runtime registry."""
        self.set_agent_enabled(agent_name, enabled=False)

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

        self._ensure_registry_entry(agent)
        registration = self._registry.get(ctx.agent)

        if registration is None or not registration.enabled:
            return RuntimeResult(
                status="error",
                trace_id=ctx.trace_id,
                agent=ctx.agent,
                output=None,
                errors=[
                    RuntimeError(
                        code="AGENT_NOT_FOUND",
                        message=f"Agent '{ctx.agent}' is not available",
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
