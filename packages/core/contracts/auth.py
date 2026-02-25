"""Auth contracts — PR-044.11 through PR-044.13.

PR-044.11: API key authentication contract + stub validator
PR-044.12: Role / permission model (RBAC contracts)
PR-044.13: Rate limiting contract + in-memory stub

These are schema-only contracts with minimal stub implementations.
Actual enforcement (middleware, DB lookup) belongs in the platform layer.
"""

from __future__ import annotations

import time
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# ── PR-044.11: API key auth ──────────────────────────────────

AuthResult = Literal["allow", "deny"]


class APIKeyInfo(BaseModel):
    """Metadata attached to a validated API key."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    key_id: str = Field(..., description="Unique key identifier (not the secret)")
    owner: str = Field(..., description="Key owner (user / service)")
    scopes: list[str] = Field(default_factory=list, description="Granted scopes")
    expires_at: str | None = Field(None, description="ISO 8601 expiry (None=never)")
    metadata: dict[str, Any] = Field(default_factory=dict)


class APIKeyValidationResult(BaseModel):
    """Result of an API key validation check."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    result: AuthResult
    key_info: APIKeyInfo | None = Field(None, description="Populated on allow")
    reason: str | None = Field(None, description="Populated on deny")


class APIKeyValidatorProtocol:
    """Abstract interface for API key validation.

    Implementations should look up the key in a store (DB, env, vault)
    and return an ``APIKeyValidationResult``.  This stub always allows.
    """

    def validate(self, raw_key: str) -> APIKeyValidationResult:
        raise NotImplementedError


class StubAPIKeyValidator(APIKeyValidatorProtocol):
    """Stub validator that allows all keys — for development only."""

    def validate(self, raw_key: str) -> APIKeyValidationResult:
        return APIKeyValidationResult(
            result="allow",
            key_info=APIKeyInfo(key_id="stub", owner="dev", scopes=["*"]),
        )


# ── PR-044.12: Role / permission model ──────────────────────


class RoleDefinition(BaseModel):
    """A named role with a set of permission strings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    role_name: str = Field(..., description="Role identifier")
    permissions: list[str] = Field(
        default_factory=list, description="Granted permissions"
    )
    description: str = Field("")


class PrincipalRoles(BaseModel):
    """Roles assigned to a principal (user/service)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    principal_id: str
    roles: list[str] = Field(default_factory=list)


def check_permission(
    principal_roles: PrincipalRoles,
    role_definitions: list[RoleDefinition],
    required_permission: str,
) -> bool:
    """Check whether *principal_roles* grant *required_permission*.

    Returns True if any role assigned to the principal contains the
    required permission string.
    """
    role_map = {r.role_name: set(r.permissions) for r in role_definitions}
    for role_name in principal_roles.roles:
        perms = role_map.get(role_name, set())
        if required_permission in perms or "*" in perms:
            return True
    return False


# ── PR-044.13: Rate limiting ────────────────────────────────


class RateLimitPolicy(BaseModel):
    """Rate limit policy definition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(..., description="Policy name")
    requests_per_minute: int = Field(60, description="Allowed requests per minute")
    burst: int = Field(10, description="Burst allowance above limit")


class RateLimitResult(BaseModel):
    """Result of a rate limit check."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    allowed: bool
    remaining: int = Field(0, description="Remaining requests in window")
    retry_after_seconds: float = Field(
        0.0, description="Seconds until next allowed request"
    )


class InMemoryRateLimiter:
    """Simple in-memory sliding-window rate limiter stub.

    Production deployments should use Redis or a distributed store.
    """

    def __init__(self, policy: RateLimitPolicy | None = None) -> None:
        self._policy = policy or RateLimitPolicy(name="default")
        self._windows: dict[str, list[float]] = {}

    def check(self, key: str) -> RateLimitResult:
        """Check whether *key* is within rate limits."""
        now = time.monotonic()
        window_start = now - 60.0
        hits = self._windows.setdefault(key, [])
        # Prune old entries
        hits[:] = [t for t in hits if t > window_start]
        limit = self._policy.requests_per_minute + self._policy.burst
        if len(hits) >= limit:
            oldest_in_window = min(hits) if hits else now
            retry_after = 60.0 - (now - oldest_in_window)
            return RateLimitResult(
                allowed=False,
                remaining=0,
                retry_after_seconds=max(retry_after, 0.0),
            )
        hits.append(now)
        return RateLimitResult(allowed=True, remaining=limit - len(hits))
