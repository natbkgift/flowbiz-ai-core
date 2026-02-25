"""Schema-only contract package for cross-repo data boundaries."""

from .agent_registry import AgentRegistration, AgentRegistrySnapshot, AgentSpec
from .health import HealthResponse
from .jobs import JobEnvelope
from .meta import RuntimeMeta
from .response import AgentResponseEnvelope, ResponseError, ToolResponseEnvelope
from .tool_registry import ToolRegistration, ToolRegistrySnapshot, ToolSpec

__all__ = [
    "AgentSpec",
    "AgentRegistration",
    "AgentRegistrySnapshot",
    "ResponseError",
    "AgentResponseEnvelope",
    "ToolResponseEnvelope",
    "HealthResponse",
    "JobEnvelope",
    "RuntimeMeta",
    "ToolSpec",
    "ToolRegistration",
    "ToolRegistrySnapshot",
]
