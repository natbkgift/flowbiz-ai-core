"""Agent-level health / status endpoint — PR-041."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(prefix="/v1/agent")


class AgentHealthResponse(BaseModel):
    """Agent subsystem health report."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: str = Field("ok", description="Agent subsystem status")
    registered_agents: int = Field(0, description="Number of registered agents")
    registered_tools: int = Field(0, description="Number of registered tools")
    details: dict[str, Any] = Field(
        default_factory=dict, description="Extra health details"
    )


# We import here to reuse the same runtime/registry singletons used by the
# agent/run endpoint.  If the runtime is not importable we still respond.
def _get_counts() -> tuple[int, int]:
    """Return (agent_count, tool_count) from runtime singletons."""
    try:
        from apps.api.routes.v1.agent import _runtime

        agents = len(_runtime._agents)
    except Exception:
        agents = 0
    try:
        from apps.api.routes.v1.tools import _tool_registry

        tools = len(_tool_registry.list_all(include_disabled=True))
    except Exception:
        tools = 0
    return agents, tools


@router.get(
    "/health",
    summary="Agent subsystem health",
    response_model=AgentHealthResponse,
)
def agent_health() -> AgentHealthResponse:
    """Lightweight health probe for the agent subsystem."""
    agents, tools = _get_counts()
    return AgentHealthResponse(
        status="ok",
        registered_agents=agents,
        registered_tools=tools,
    )
