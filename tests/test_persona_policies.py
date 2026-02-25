"""Tests for docs agent safe IO rules and persona policies."""

from __future__ import annotations

from packages.core.persona_policies import (
    ALL_AGENT_POLICIES,
    CORE_AGENT_POLICY,
    DOCS_AGENT_POLICY,
    INFRA_AGENT_POLICY,
)
from packages.core.tool_permission_checker import check_tool_permission
from packages.core.tools.permissions import Permission, ToolPermissions


class TestDocsAgentPolicy:
    """Verify docs persona enforces safe IO — no shell, no net, no DB."""

    def test_docs_allows_read_fs(self) -> None:
        tp = ToolPermissions(required_permissions=[Permission.READ_FS])
        result = check_tool_permission(DOCS_AGENT_POLICY, tp, "read_file")
        assert result.allowed is True

    def test_docs_allows_write_fs(self) -> None:
        tp = ToolPermissions(required_permissions=[Permission.WRITE_FS])
        result = check_tool_permission(DOCS_AGENT_POLICY, tp, "write_md")
        assert result.allowed is True

    def test_docs_denies_exec_shell(self) -> None:
        tp = ToolPermissions(required_permissions=[Permission.EXEC_SHELL])
        result = check_tool_permission(DOCS_AGENT_POLICY, tp, "bash")
        assert result.allowed is False
        assert "EXEC_SHELL" in result.reason

    def test_docs_denies_network(self) -> None:
        tp = ToolPermissions(required_permissions=[Permission.NET_HTTP])
        result = check_tool_permission(DOCS_AGENT_POLICY, tp, "curl")
        assert result.allowed is False

    def test_docs_denies_db_read(self) -> None:
        tp = ToolPermissions(required_permissions=[Permission.DB_READ])
        result = check_tool_permission(DOCS_AGENT_POLICY, tp, "query")
        assert result.allowed is False

    def test_docs_denies_db_write(self) -> None:
        tp = ToolPermissions(required_permissions=[Permission.DB_WRITE])
        result = check_tool_permission(DOCS_AGENT_POLICY, tp, "insert")
        assert result.allowed is False

    def test_docs_denies_read_env(self) -> None:
        tp = ToolPermissions(required_permissions=[Permission.READ_ENV])
        result = check_tool_permission(DOCS_AGENT_POLICY, tp, "env_reader")
        assert result.allowed is False


class TestInfraAgentPolicy:
    """Verify infra persona has broader access."""

    def test_infra_allows_shell(self) -> None:
        tp = ToolPermissions(required_permissions=[Permission.EXEC_SHELL])
        result = check_tool_permission(INFRA_AGENT_POLICY, tp, "deploy")
        assert result.allowed is True

    def test_infra_allows_network(self) -> None:
        tp = ToolPermissions(required_permissions=[Permission.NET_HTTP])
        result = check_tool_permission(INFRA_AGENT_POLICY, tp, "healthcheck")
        assert result.allowed is True

    def test_infra_denies_db_write(self) -> None:
        tp = ToolPermissions(required_permissions=[Permission.DB_WRITE])
        result = check_tool_permission(INFRA_AGENT_POLICY, tp, "migrate")
        assert result.allowed is False


class TestCoreAgentPolicy:
    def test_core_allows_read_fs(self) -> None:
        tp = ToolPermissions(required_permissions=[Permission.READ_FS])
        result = check_tool_permission(CORE_AGENT_POLICY, tp, "scan")
        assert result.allowed is True

    def test_core_denies_shell(self) -> None:
        tp = ToolPermissions(required_permissions=[Permission.EXEC_SHELL])
        result = check_tool_permission(CORE_AGENT_POLICY, tp, "bash")
        assert result.allowed is False

    def test_core_denies_write_fs(self) -> None:
        tp = ToolPermissions(required_permissions=[Permission.WRITE_FS])
        result = check_tool_permission(CORE_AGENT_POLICY, tp, "overwrite")
        assert result.allowed is False


class TestAllPoliciesDict:
    def test_contains_three(self) -> None:
        assert set(ALL_AGENT_POLICIES.keys()) == {"core", "infra", "docs"}

    def test_docs_matches_constant(self) -> None:
        assert ALL_AGENT_POLICIES["docs"] is DOCS_AGENT_POLICY

    def test_infra_matches_constant(self) -> None:
        assert ALL_AGENT_POLICIES["infra"] is INFRA_AGENT_POLICY

    def test_core_matches_constant(self) -> None:
        assert ALL_AGENT_POLICIES["core"] is CORE_AGENT_POLICY
