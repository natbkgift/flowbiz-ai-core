"""Tool permission checker for persona-based authorization.

Evaluates whether a tool execution is allowed given the agent's
persona policy and the tool's declared permission requirements.
"""

from __future__ import annotations

from packages.core.tools.permissions import (
    AgentPolicy,
    PolicyDecision,
    ToolPermissions,
)


def check_tool_permission(
    policy: AgentPolicy,
    tool_permissions: ToolPermissions,
    tool_name: str,
) -> PolicyDecision:
    """Decide whether *tool_name* may execute under *policy*.

    Checks are applied in this order (deny-first):

    1. **Tool allowlist** — if the policy defines ``allowed_tools`` and
       *tool_name* is not in the list, deny immediately.
    2. **Required permissions** — every permission in
       ``tool_permissions.required_permissions`` must appear in
       ``policy.allowed_permissions``.  If any is missing, deny.
    3. Otherwise, allow.

    Returns a :class:`PolicyDecision` with *allowed* and a human-readable
    *reason*.
    """
    # 1) Tool allowlist check
    if policy.allowed_tools and tool_name not in policy.allowed_tools:
        return PolicyDecision(
            allowed=False,
            reason=f"Tool '{tool_name}' is not in the allowlist for persona '{policy.persona}'",
        )

    # 2) Required permission check
    allowed_set = set(policy.allowed_permissions)
    missing = [
        p.value
        for p in tool_permissions.required_permissions
        if p not in allowed_set
    ]
    if missing:
        return PolicyDecision(
            allowed=False,
            reason=f"Missing required permissions: {', '.join(sorted(missing))}",
        )

    # 3) All checks passed
    return PolicyDecision(allowed=True, reason="All checks passed")
