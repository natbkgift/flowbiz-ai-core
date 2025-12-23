"""Tests for permission model schemas.

These tests verify the permission model types defined in
packages/core/tools/permissions.py are correctly structured.

Note: These are schema/type tests only. No runtime enforcement is tested
since enforcement is not implemented in this PR (design-only).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.tools.permissions import (
    AgentPolicy,
    Permission,
    PolicyDecision,
    ToolPermissions,
)


class TestPermissionEnum:
    """Test the Permission enum."""

    def test_permission_enum_values(self):
        """Verify all expected permissions are defined."""
        expected = {
            "READ_FS",
            "WRITE_FS",
            "NET_HTTP",
            "EXEC_SHELL",
            "READ_ENV",
            "DB_READ",
            "DB_WRITE",
        }
        actual = {p.value for p in Permission}
        assert actual == expected

    def test_permission_enum_access(self):
        """Test permission enum can be accessed by name."""
        assert Permission.READ_FS.value == "READ_FS"
        assert Permission.NET_HTTP.value == "NET_HTTP"
        assert Permission.EXEC_SHELL.value == "EXEC_SHELL"


class TestToolPermissions:
    """Test the ToolPermissions schema."""

    def test_tool_permissions_empty_defaults(self):
        """Test ToolPermissions with no permissions specified."""
        perms = ToolPermissions()
        assert perms.required_permissions == []
        assert perms.optional_permissions == []

    def test_tool_permissions_with_required(self):
        """Test ToolPermissions with required permissions."""
        perms = ToolPermissions(
            required_permissions=[Permission.READ_FS, Permission.NET_HTTP]
        )
        assert len(perms.required_permissions) == 2
        assert Permission.READ_FS in perms.required_permissions
        assert Permission.NET_HTTP in perms.required_permissions
        assert perms.optional_permissions == []

    def test_tool_permissions_with_optional(self):
        """Test ToolPermissions with optional permissions."""
        perms = ToolPermissions(
            optional_permissions=[Permission.WRITE_FS, Permission.DB_WRITE]
        )
        assert len(perms.optional_permissions) == 2
        assert Permission.WRITE_FS in perms.optional_permissions
        assert Permission.DB_WRITE in perms.optional_permissions
        assert perms.required_permissions == []

    def test_tool_permissions_with_both(self):
        """Test ToolPermissions with both required and optional."""
        perms = ToolPermissions(
            required_permissions=[Permission.READ_FS],
            optional_permissions=[Permission.WRITE_FS],
        )
        assert len(perms.required_permissions) == 1
        assert len(perms.optional_permissions) == 1
        assert Permission.READ_FS in perms.required_permissions
        assert Permission.WRITE_FS in perms.optional_permissions

    def test_tool_permissions_immutable(self):
        """Test ToolPermissions is frozen/immutable."""
        perms = ToolPermissions(required_permissions=[Permission.READ_FS])
        with pytest.raises((ValidationError, AttributeError)):
            perms.required_permissions = [Permission.NET_HTTP]

    def test_tool_permissions_serialization(self):
        """Test ToolPermissions can be serialized."""
        perms = ToolPermissions(
            required_permissions=[Permission.READ_FS, Permission.NET_HTTP],
            optional_permissions=[Permission.WRITE_FS],
        )
        data = perms.model_dump()
        assert "required_permissions" in data
        assert "optional_permissions" in data
        assert len(data["required_permissions"]) == 2
        assert len(data["optional_permissions"]) == 1


class TestAgentPolicy:
    """Test the AgentPolicy schema."""

    def test_agent_policy_minimal(self):
        """Test AgentPolicy with minimal fields."""
        policy = AgentPolicy(persona="core")
        assert policy.persona == "core"
        assert policy.allowed_permissions == []
        assert policy.allowed_tools == []

    def test_agent_policy_with_permissions(self):
        """Test AgentPolicy with allowed permissions."""
        policy = AgentPolicy(
            persona="core",
            allowed_permissions=[Permission.NET_HTTP, Permission.READ_ENV],
        )
        assert policy.persona == "core"
        assert len(policy.allowed_permissions) == 2
        assert Permission.NET_HTTP in policy.allowed_permissions
        assert Permission.READ_ENV in policy.allowed_permissions

    def test_agent_policy_with_tool_allowlist(self):
        """Test AgentPolicy with tool allowlist."""
        policy = AgentPolicy(
            persona="core",
            allowed_permissions=[Permission.NET_HTTP],
            allowed_tools=["web_search", "fetch_api"],
        )
        assert policy.persona == "core"
        assert policy.allowed_tools == ["web_search", "fetch_api"]

    def test_agent_policy_immutable(self):
        """Test AgentPolicy is frozen/immutable."""
        policy = AgentPolicy(persona="core")
        with pytest.raises((ValidationError, AttributeError)):
            policy.persona = "infra"

    def test_agent_policy_serialization(self):
        """Test AgentPolicy can be serialized."""
        policy = AgentPolicy(
            persona="infra",
            allowed_permissions=[Permission.EXEC_SHELL, Permission.READ_FS],
            allowed_tools=["deploy", "restart"],
        )
        data = policy.model_dump()
        assert data["persona"] == "infra"
        assert len(data["allowed_permissions"]) == 2
        assert data["allowed_tools"] == ["deploy", "restart"]


class TestPolicyDecision:
    """Test the PolicyDecision schema."""

    def test_policy_decision_allowed(self):
        """Test PolicyDecision for allowed execution."""
        decision = PolicyDecision(allowed=True, reason="All checks passed")
        assert decision.allowed is True
        assert decision.reason == "All checks passed"

    def test_policy_decision_denied(self):
        """Test PolicyDecision for denied execution."""
        decision = PolicyDecision(
            allowed=False, reason="Missing required permission: EXEC_SHELL"
        )
        assert decision.allowed is False
        assert "EXEC_SHELL" in decision.reason

    def test_policy_decision_default_reason(self):
        """Test PolicyDecision has empty default reason."""
        decision = PolicyDecision(allowed=True)
        assert decision.allowed is True
        assert decision.reason == ""

    def test_policy_decision_immutable(self):
        """Test PolicyDecision is frozen/immutable."""
        decision = PolicyDecision(allowed=True, reason="ok")
        with pytest.raises((ValidationError, AttributeError)):
            decision.allowed = False

    def test_policy_decision_serialization(self):
        """Test PolicyDecision can be serialized."""
        decision = PolicyDecision(allowed=False, reason="Test denial")
        data = decision.model_dump()
        assert data["allowed"] is False
        assert data["reason"] == "Test denial"


class TestPermissionModelIntegration:
    """Integration tests for permission model types working together."""

    def test_core_persona_example(self):
        """Test a complete core persona policy example."""
        # Define a tool's permissions
        tool_perms = ToolPermissions(
            required_permissions=[Permission.NET_HTTP],
            optional_permissions=[Permission.READ_ENV],
        )

        # Define a core persona policy
        policy = AgentPolicy(
            persona="core",
            allowed_permissions=[Permission.NET_HTTP, Permission.READ_ENV],
            allowed_tools=["web_search"],
        )

        # Both schemas are valid
        assert len(tool_perms.required_permissions) == 1
        assert len(policy.allowed_permissions) == 2

    def test_infra_persona_example(self):
        """Test a complete infra persona policy example."""
        tool_perms = ToolPermissions(
            required_permissions=[Permission.EXEC_SHELL, Permission.READ_FS]
        )

        policy = AgentPolicy(
            persona="infra",
            allowed_permissions=[
                Permission.EXEC_SHELL,
                Permission.READ_FS,
                Permission.WRITE_FS,
                Permission.NET_HTTP,
            ],
        )

        assert Permission.EXEC_SHELL in tool_perms.required_permissions
        assert Permission.EXEC_SHELL in policy.allowed_permissions

    def test_docs_persona_example(self):
        """Test a complete docs persona policy example."""
        tool_perms = ToolPermissions(
            required_permissions=[Permission.READ_FS, Permission.WRITE_FS]
        )

        policy = AgentPolicy(
            persona="docs",
            allowed_permissions=[Permission.READ_FS, Permission.WRITE_FS],
            allowed_tools=["markdown_lint", "spell_check"],
        )

        assert len(tool_perms.required_permissions) == 2
        assert len(policy.allowed_tools) == 2
