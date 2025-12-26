"""Agent Runtime Skeleton - PR-022.

Minimal runtime plumbing for agent execution via HTTP.
"""

from .agent_base import AgentBase
from .context import RuntimeContext
from .request import RuntimeRequest
from .result import RuntimeResult
from .runtime import AgentRuntime

__all__ = [
    "AgentBase",
    "RuntimeContext",
    "RuntimeRequest",
    "RuntimeResult",
    "AgentRuntime",
]
