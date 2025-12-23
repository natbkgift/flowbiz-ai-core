"""Contract-only authorization hook for tools and personas.

This module defines the authorization contract without any runtime enforcement.
It is intentionally side-effect free and deterministic. The implementation
returns an allow decision to avoid breaking existing runtime behavior. Future
work (PR-030) will integrate policy evaluation before tool execution.
"""

from __future__ import annotations

from .base import ToolBase
from .context import ToolContext
from .permissions import AgentPolicy, PolicyDecision

__all__ = ["authorize"]


def authorize(tool: ToolBase, ctx: ToolContext, policy: AgentPolicy) -> PolicyDecision:
    """Authorize tool execution against a persona policy (design-only).

    This is a pure contract stub that will be wired into the execution pipeline
    in a future PR. No checks are performed today; it always returns an allow
    decision to preserve current behavior.

    Args:
        tool: Tool requesting execution.
        ctx: Tool execution context (unused in design-only contract).
        policy: Agent policy describing allowed permissions and tool allowlists.

    Returns:
        PolicyDecision: Always an allow decision with a design-only reason.
    """

    _ = (tool, ctx, policy)
    return PolicyDecision(allowed=True, reason="design-only: not enforced")
