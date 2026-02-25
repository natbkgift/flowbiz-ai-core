"""Tests for tool permission checker (persona-based authorization)."""

from __future__ import annotations

from packages.core.tool_permission_checker import check_tool_permission
from packages.core.tools.permissions import (
    AgentPolicy,
    Permission,
    ToolPermissions,
)


class TestCheckToolPermission:
    """Tests for the check_tool_permission function."""

    # ── allow cases ───────────────────────────────────────────────────

    def test_allow_when_no_restrictions(self) -> None:
        policy = AgentPolicy(persona="core")
        tool_perms = ToolPermissions()
        result = check_tool_permission(policy, tool_perms, "anything")
        assert result.allowed is True

    def test_allow_when_permissions_match(self) -> None:
        policy = AgentPolicy(
            persona="infra",
            allowed_permissions=[Permission.EXEC_SHELL, Permission.READ_FS],
        )
        tool_perms = ToolPermissions(
            required_permissions=[Permission.READ_FS],
        )
        result = check_tool_permission(policy, tool_perms, "ls_tool")
        assert result.allowed is True

    def test_allow_when_tool_in_allowlist(self) -> None:
        policy = AgentPolicy(
            persona="core",
            allowed_tools=["search", "fetch"],
            allowed_permissions=[Permission.NET_HTTP],
        )
        tool_perms = ToolPermissions(
            required_permissions=[Permission.NET_HTTP],
        )
        result = check_tool_permission(policy, tool_perms, "search")
        assert result.allowed is True

    def test_allow_empty_allowlist_means_all_tools(self) -> None:
        """Empty allowed_tools list means any tool name is acceptable."""
        policy = AgentPolicy(
            persona="docs",
            allowed_permissions=[Permission.READ_FS],
        )
        tool_perms = ToolPermissions(
            required_permissions=[Permission.READ_FS],
        )
        result = check_tool_permission(policy, tool_perms, "random_tool")
        assert result.allowed is True

    def test_allow_reason_message(self) -> None:
        policy = AgentPolicy(persona="core")
        result = check_tool_permission(policy, ToolPermissions(), "t")
        assert result.reason == "All checks passed"

    # ── deny: tool not in allowlist ──────────────────────────────────

    def test_deny_tool_not_in_allowlist(self) -> None:
        policy = AgentPolicy(
            persona="docs",
            allowed_tools=["spell_check"],
        )
        result = check_tool_permission(policy, ToolPermissions(), "rm_tool")
        assert result.allowed is False
        assert "allowlist" in result.reason
        assert "rm_tool" in result.reason

    # ── deny: missing permissions ─────────────────────────────────────

    def test_deny_missing_single_permission(self) -> None:
        policy = AgentPolicy(
            persona="docs",
            allowed_permissions=[Permission.READ_FS],
        )
        tool_perms = ToolPermissions(
            required_permissions=[Permission.EXEC_SHELL],
        )
        result = check_tool_permission(policy, tool_perms, "run_cmd")
        assert result.allowed is False
        assert "EXEC_SHELL" in result.reason

    def test_deny_missing_multiple_permissions(self) -> None:
        policy = AgentPolicy(
            persona="docs",
            allowed_permissions=[Permission.READ_FS],
        )
        tool_perms = ToolPermissions(
            required_permissions=[
                Permission.EXEC_SHELL,
                Permission.WRITE_FS,
            ],
        )
        result = check_tool_permission(policy, tool_perms, "dangerous")
        assert result.allowed is False
        assert "EXEC_SHELL" in result.reason
        assert "WRITE_FS" in result.reason

    # ── ordering: allowlist checked before permissions ─────────────────

    def test_allowlist_checked_before_permissions(self) -> None:
        """If tool is not in allowlist, deny even if permissions match."""
        policy = AgentPolicy(
            persona="core",
            allowed_tools=["safe_tool"],
            allowed_permissions=[Permission.EXEC_SHELL],
        )
        tool_perms = ToolPermissions(
            required_permissions=[Permission.EXEC_SHELL],
        )
        result = check_tool_permission(policy, tool_perms, "evil_tool")
        assert result.allowed is False
        assert "allowlist" in result.reason

    # ── optional permissions do not block ──────────────────────────────

    def test_optional_permissions_do_not_affect_decision(self) -> None:
        """Optional permissions on the tool should not cause denial."""
        policy = AgentPolicy(
            persona="core",
            allowed_permissions=[Permission.NET_HTTP],
        )
        tool_perms = ToolPermissions(
            required_permissions=[Permission.NET_HTTP],
            optional_permissions=[Permission.DB_WRITE],  # not granted
        )
        result = check_tool_permission(policy, tool_perms, "api_call")
        assert result.allowed is True

    # ── persona integration examples ──────────────────────────────────

    def test_infra_persona_allows_shell(self) -> None:
        policy = AgentPolicy(
            persona="infra",
            allowed_permissions=[
                Permission.EXEC_SHELL,
                Permission.READ_FS,
                Permission.WRITE_FS,
                Permission.NET_HTTP,
            ],
        )
        tool_perms = ToolPermissions(
            required_permissions=[Permission.EXEC_SHELL, Permission.READ_FS],
        )
        result = check_tool_permission(policy, tool_perms, "deploy_script")
        assert result.allowed is True

    def test_docs_persona_denies_shell(self) -> None:
        policy = AgentPolicy(
            persona="docs",
            allowed_permissions=[Permission.READ_FS, Permission.WRITE_FS],
        )
        tool_perms = ToolPermissions(
            required_permissions=[Permission.EXEC_SHELL],
        )
        result = check_tool_permission(policy, tool_perms, "run_cmd")
        assert result.allowed is False
        assert "EXEC_SHELL" in result.reason
