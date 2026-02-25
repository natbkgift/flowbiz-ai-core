"""Infra agent ops guardrails.

Defines an allowlist of safe shell command prefixes that infra agents
can execute, and a checker function that validates commands before
execution.  Only compose, health-check, and log-viewing commands are
allowed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from pydantic import BaseModel, ConfigDict, Field

# ── contracts ──────────────────────────────────────────────────────────────


class OpsCommandResult(BaseModel):
    """Outcome of validating a shell command against the ops allowlist."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    allowed: bool = Field(..., description="Whether the command is allowed")
    command: str = Field(..., description="The command that was checked")
    reason: str = Field(default="", description="Explanation of decision")


# ── default allowlist ──────────────────────────────────────────────────────

DEFAULT_ALLOWED_PREFIXES: tuple[str, ...] = (
    "docker compose",
    "docker-compose",
    "docker ps",
    "docker logs",
    "docker inspect",
    "docker stats",
    "docker top",
    "docker health",
    "curl",
    "wget",
    "systemctl status",
    "journalctl",
    "tail",
    "head",
    "cat",
    "grep",
    "ls",
    "df",
    "du",
    "free",
    "uptime",
    "ping",
    "dig",
    "nslookup",
    "ss",
    "netstat",
)
"""Command prefixes considered safe for infra ops work."""

# ── patterns that are always denied ───────────────────────────────────────

_DENY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\brm\s+-rf\b", re.IGNORECASE),
    re.compile(r"\bmkfs\b", re.IGNORECASE),
    re.compile(r"\bdd\s+if=", re.IGNORECASE),
    re.compile(r"\b(shutdown|reboot|halt|poweroff)\b", re.IGNORECASE),
    re.compile(r">\s*/dev/[a-z]", re.IGNORECASE),
    re.compile(r"\bchmod\s+777\b", re.IGNORECASE),
)


# ── checker ────────────────────────────────────────────────────────────────


@dataclass
class OpsGuardrail:
    """Validates shell commands against an infra-ops allowlist."""

    allowed_prefixes: tuple[str, ...] = field(
        default_factory=lambda: DEFAULT_ALLOWED_PREFIXES
    )

    def check(self, command: str) -> OpsCommandResult:
        """Return whether *command* is allowed for infra ops."""
        stripped = command.strip()

        # Deny-list takes priority
        for pattern in _DENY_PATTERNS:
            if pattern.search(stripped):
                return OpsCommandResult(
                    allowed=False,
                    command=stripped,
                    reason=f"Command matches deny pattern: {pattern.pattern}",
                )

        # Allowlist prefix check (word-boundary aware)
        lower = stripped.lower()
        for prefix in self.allowed_prefixes:
            p = prefix.lower()
            if lower == p or lower.startswith(p + " "):
                return OpsCommandResult(
                    allowed=True,
                    command=stripped,
                    reason=f"Matched allowed prefix: {prefix}",
                )

        return OpsCommandResult(
            allowed=False,
            command=stripped,
            reason="Command does not match any allowed prefix",
        )
