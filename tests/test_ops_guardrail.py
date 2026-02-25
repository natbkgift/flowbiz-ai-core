"""Tests for infra agent ops guardrails."""

from __future__ import annotations

import pytest

from packages.core.ops_guardrail import (
    DEFAULT_ALLOWED_PREFIXES,
    OpsCommandResult,
    OpsGuardrail,
)


class TestOpsCommandResultContract:
    def test_frozen(self) -> None:
        r = OpsCommandResult(allowed=True, command="ls", reason="ok")
        with pytest.raises(Exception):
            r.allowed = False  # type: ignore[misc]

    def test_forbid_extra(self) -> None:
        with pytest.raises(Exception):
            OpsCommandResult(allowed=True, command="ls", extra="x")  # type: ignore[call-arg]


class TestOpsGuardrailAllowed:
    """Commands that SHOULD be allowed."""

    @pytest.mark.parametrize(
        "cmd",
        [
            "docker compose up -d",
            "docker-compose ps",
            "docker compose logs api",
            "docker ps",
            "docker logs my-container",
            "docker inspect abc123",
            "docker stats --no-stream",
            "curl http://localhost:8000/healthz",
            "tail -f /var/log/syslog",
            "cat /etc/hostname",
            "grep error /var/log/app.log",
            "ls -la /opt/app",
            "df -h",
            "du -sh /var/log",
            "free -m",
            "uptime",
            "ping -c 3 google.com",
            "dig flowbiz.cloud",
            "ss -tlnp",
            "systemctl status nginx",
            "journalctl -u nginx --since today",
        ],
    )
    def test_allowed_command(self, cmd: str) -> None:
        g = OpsGuardrail()
        result = g.check(cmd)
        assert result.allowed is True, f"Expected allowed: {cmd!r} — {result.reason}"

    def test_allowed_prefix_in_reason(self) -> None:
        g = OpsGuardrail()
        result = g.check("docker compose restart")
        assert "docker compose" in result.reason.lower()


class TestOpsGuardrailDenied:
    """Commands that SHOULD be denied."""

    @pytest.mark.parametrize(
        "cmd",
        [
            "rm -rf /",
            "mkfs.ext4 /dev/sda1",
            "dd if=/dev/zero of=/dev/sda",
            "shutdown -h now",
            "reboot",
            "halt",
            "poweroff",
            "chmod 777 /etc/shadow",
            "> /dev/sda",
        ],
    )
    def test_denied_dangerous_command(self, cmd: str) -> None:
        g = OpsGuardrail()
        result = g.check(cmd)
        assert result.allowed is False, f"Expected denied: {cmd!r}"

    @pytest.mark.parametrize(
        "cmd",
        [
            "python -c 'import os; os.system(\"rm -rf /\")'",
            "npm install malware",
            "apt-get install foo",
            "pip install evil",
            "ssh user@host",
        ],
    )
    def test_denied_unknown_command(self, cmd: str) -> None:
        g = OpsGuardrail()
        result = g.check(cmd)
        assert result.allowed is False

    def test_denied_reason_message(self) -> None:
        g = OpsGuardrail()
        result = g.check("npm start")
        assert "does not match" in result.reason


class TestOpsGuardrailCustomPrefixes:
    def test_custom_prefix(self) -> None:
        g = OpsGuardrail(allowed_prefixes=("kubectl",))
        assert g.check("kubectl get pods").allowed is True
        assert g.check("docker ps").allowed is False

    def test_deny_pattern_overrides_custom_prefix(self) -> None:
        """Even if prefix matches, deny patterns should still block."""
        g = OpsGuardrail(allowed_prefixes=("rm",))
        result = g.check("rm -rf /important")
        assert result.allowed is False


class TestDefaultAllowedPrefixes:
    def test_has_compose_prefixes(self) -> None:
        assert "docker compose" in DEFAULT_ALLOWED_PREFIXES
        assert "docker-compose" in DEFAULT_ALLOWED_PREFIXES

    def test_has_health_prefixes(self) -> None:
        assert "curl" in DEFAULT_ALLOWED_PREFIXES
        assert "ping" in DEFAULT_ALLOWED_PREFIXES

    def test_has_log_prefixes(self) -> None:
        assert "docker logs" in DEFAULT_ALLOWED_PREFIXES
        assert "tail" in DEFAULT_ALLOWED_PREFIXES
        assert "journalctl" in DEFAULT_ALLOWED_PREFIXES
