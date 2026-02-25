"""Pre-built persona policies.

Canonical ``AgentPolicy`` instances for each persona, encoding the
principle-of-least-privilege rules agreed upon in the roadmap.

* **docs** — read/write filesystem only; no shell, no network, no DB.
* **infra** — filesystem + shell + network (compose/health/logs tasks).
* **core** — filesystem read + network + env read; no shell.
"""

from __future__ import annotations

from packages.core.tools.permissions import AgentPolicy, Permission

# ── Docs persona policy ──────────────────────────────────────────────────

DOCS_AGENT_POLICY = AgentPolicy(
    persona="docs",
    allowed_permissions=[
        Permission.READ_FS,
        Permission.WRITE_FS,
    ],
    # No shell, no network, no DB access for docs agents.
)
"""Docs agents may only read and write files."""

# ── Infra persona policy (preview — full rules in PR-034) ────────────────

INFRA_AGENT_POLICY = AgentPolicy(
    persona="infra",
    allowed_permissions=[
        Permission.READ_FS,
        Permission.WRITE_FS,
        Permission.NET_HTTP,
        Permission.EXEC_SHELL,
        Permission.READ_ENV,
    ],
)
"""Infra agents can run shell commands, access the network, and read env vars."""

# ── Core persona policy ──────────────────────────────────────────────────

CORE_AGENT_POLICY = AgentPolicy(
    persona="core",
    allowed_permissions=[
        Permission.READ_FS,
        Permission.NET_HTTP,
        Permission.READ_ENV,
    ],
)
"""Core agents can read files, make HTTP calls, and read env vars."""

ALL_AGENT_POLICIES: dict[str, AgentPolicy] = {
    "docs": DOCS_AGENT_POLICY,
    "infra": INFRA_AGENT_POLICY,
    "core": CORE_AGENT_POLICY,
}
