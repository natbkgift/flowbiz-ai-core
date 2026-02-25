"""Agent tools listing endpoint — PR-040."""

from __future__ import annotations

from fastapi import APIRouter

from packages.core.contracts.tool_registry import ToolRegistrySnapshot
from packages.core.tool_registry import InMemoryToolRegistry

router = APIRouter(prefix="/v1/agent")

# Shared singleton — in production this would be injected via DI.
_tool_registry = InMemoryToolRegistry()


@router.get(
    "/tools",
    summary="List registered tools",
    response_model=ToolRegistrySnapshot,
)
def list_tools(include_disabled: bool = False) -> ToolRegistrySnapshot:
    """Return a snapshot of all registered tools."""
    tools = _tool_registry.list_all(include_disabled=include_disabled)
    return ToolRegistrySnapshot(tools=tools)


def get_tool_registry() -> InMemoryToolRegistry:
    """Return the module-level tool registry (useful for tests)."""
    return _tool_registry
