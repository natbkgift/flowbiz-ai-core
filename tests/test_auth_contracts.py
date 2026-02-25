"""Tests for auth contracts — PR-044.11 through PR-044.13."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.contracts.auth import (
    APIKeyInfo,
    APIKeyValidationResult,
    InMemoryRateLimiter,
    PrincipalRoles,
    RateLimitPolicy,
    RateLimitResult,
    RoleDefinition,
    StubAPIKeyValidator,
    check_permission,
)


# ── API key auth (PR-044.11) ─────────────────────────────────


class TestAPIKeyContracts:
    def test_key_info_frozen(self) -> None:
        k = APIKeyInfo(key_id="k1", owner="alice")
        with pytest.raises(ValidationError):
            k.key_id = "k2"  # type: ignore[misc]

    def test_validation_allow(self) -> None:
        r = APIKeyValidationResult(
            result="allow",
            key_info=APIKeyInfo(key_id="k1", owner="alice", scopes=["read"]),
        )
        assert r.result == "allow"
        assert r.key_info is not None

    def test_validation_deny(self) -> None:
        r = APIKeyValidationResult(result="deny", reason="expired")
        assert r.reason == "expired"

    def test_stub_validator_allows(self) -> None:
        v = StubAPIKeyValidator()
        result = v.validate("any-key")
        assert result.result == "allow"
        assert result.key_info is not None
        assert result.key_info.key_id == "stub"


# ── Role / permission model (PR-044.12) ──────────────────────


class TestRBACContracts:
    def test_role_definition(self) -> None:
        r = RoleDefinition(role_name="admin", permissions=["read", "write"])
        assert len(r.permissions) == 2

    def test_principal_roles(self) -> None:
        p = PrincipalRoles(principal_id="u1", roles=["admin"])
        assert p.roles == ["admin"]

    def test_check_permission_granted(self) -> None:
        roles = [RoleDefinition(role_name="editor", permissions=["read", "write"])]
        principal = PrincipalRoles(principal_id="u1", roles=["editor"])
        assert check_permission(principal, roles, "write") is True

    def test_check_permission_denied(self) -> None:
        roles = [RoleDefinition(role_name="viewer", permissions=["read"])]
        principal = PrincipalRoles(principal_id="u1", roles=["viewer"])
        assert check_permission(principal, roles, "write") is False

    def test_wildcard_permission(self) -> None:
        roles = [RoleDefinition(role_name="superadmin", permissions=["*"])]
        principal = PrincipalRoles(principal_id="u1", roles=["superadmin"])
        assert check_permission(principal, roles, "anything") is True

    def test_no_roles_denies(self) -> None:
        roles = [RoleDefinition(role_name="admin", permissions=["read"])]
        principal = PrincipalRoles(principal_id="u1", roles=[])
        assert check_permission(principal, roles, "read") is False


# ── Rate limiting (PR-044.13) ────────────────────────────────


class TestRateLimiting:
    def test_policy_defaults(self) -> None:
        p = RateLimitPolicy(name="default")
        assert p.requests_per_minute == 60
        assert p.burst == 10

    def test_allows_within_limit(self) -> None:
        limiter = InMemoryRateLimiter(
            RateLimitPolicy(name="test", requests_per_minute=5, burst=0)
        )
        result = limiter.check("user-1")
        assert result.allowed is True
        assert result.remaining == 4

    def test_blocks_over_limit(self) -> None:
        policy = RateLimitPolicy(name="strict", requests_per_minute=2, burst=0)
        limiter = InMemoryRateLimiter(policy)
        limiter.check("user-1")
        limiter.check("user-1")
        result = limiter.check("user-1")
        assert result.allowed is False

    def test_different_keys_independent(self) -> None:
        policy = RateLimitPolicy(name="t", requests_per_minute=1, burst=0)
        limiter = InMemoryRateLimiter(policy)
        limiter.check("a")
        result = limiter.check("b")
        assert result.allowed is True

    def test_result_schema(self) -> None:
        r = RateLimitResult(allowed=True, remaining=5)
        assert r.retry_after_seconds == 0.0
