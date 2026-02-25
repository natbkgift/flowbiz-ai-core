from __future__ import annotations

import json

import pytest

from packages.core import reset_settings_cache
from packages.core.cli import main


class TestCoreCli:
    def teardown_method(self) -> None:
        reset_settings_cache()

    def test_main_without_command_prints_help_and_returns_1(self, capsys) -> None:
        assert main([]) == 1
        out = capsys.readouterr().out
        assert "FlowBiz AI Core developer CLI" in out
        assert "usage:" in out

    def test_version_json(self, monkeypatch, capsys) -> None:
        monkeypatch.setenv("FLOWBIZ_VERSION", "1.2.3")
        monkeypatch.setenv("FLOWBIZ_GIT_SHA", "abc123")
        monkeypatch.setenv("FLOWBIZ_BUILD_TIME", "2026-02-25T00:00:00Z")

        assert main(["version", "--format", "json"]) == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["version"] == "1.2.3"
        assert payload["git_sha"] == "abc123"
        assert payload["build_time"] == "2026-02-25T00:00:00Z"

    def test_meta_text_uses_settings(self, monkeypatch, capsys) -> None:
        monkeypatch.setenv("APP_NAME", "FlowBiz Test Core")
        monkeypatch.setenv("APP_ENV", "test")
        monkeypatch.setenv("APP_VERSION", "9.9.9")
        reset_settings_cache()

        assert main(["meta"]) == 0
        out = capsys.readouterr().out
        assert "flowbiz-core meta" in out
        assert "service: FlowBiz Test Core" in out
        assert "env: test" in out
        assert "version: 9.9.9" in out

    def test_agents_excludes_disabled_by_default(self, capsys) -> None:
        assert main(["agents", "--format", "json"]) == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["count"] == 1
        assert [agent["agent_name"] for agent in payload["agents"]] == ["default"]

    def test_agents_include_disabled(self, capsys) -> None:
        assert main(["agents", "--include-disabled", "--format", "json"]) == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["count"] == 2
        names = [agent["agent_name"] for agent in payload["agents"]]
        assert names == ["default", "docs"]
        docs_entry = next(agent for agent in payload["agents"] if agent["agent_name"] == "docs")
        assert docs_entry["enabled"] is False

    def test_tools_include_disabled_text(self, capsys) -> None:
        assert main(["tools", "--include-disabled"]) == 0
        out = capsys.readouterr().out
        assert "flowbiz-core tools" in out
        assert "dummy.echo" in out
        assert "system.health" in out
        assert "count: 2" in out

    def test_invalid_command_exits_with_argparse_error(self) -> None:
        with pytest.raises(SystemExit) as excinfo:
            main(["nope"])
        assert excinfo.value.code == 2
