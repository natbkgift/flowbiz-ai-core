"""Tests for agent config contracts and loader."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.agent_config_loader import (
    load_agent_config,
    load_agent_config_set,
    load_agent_configs_from_list,
)
from packages.core.contracts.agent_config import AgentConfig, AgentConfigSet


# ── contract tests ────────────────────────────────────────────────────────


class TestAgentConfigContract:
    def test_minimal_config(self) -> None:
        cfg = AgentConfig(agent_name="echo", persona="core")
        assert cfg.agent_name == "echo"
        assert cfg.persona == "core"
        assert cfg.enabled is True
        assert cfg.tags == []
        assert cfg.allowed_tools == []

    def test_full_config(self) -> None:
        cfg = AgentConfig(
            agent_name="writer",
            persona="docs",
            description="Writes docs",
            enabled=False,
            tags=["md"],
            allowed_tools=["spell_check"],
        )
        assert cfg.description == "Writes docs"
        assert cfg.enabled is False

    def test_frozen(self) -> None:
        cfg = AgentConfig(agent_name="a", persona="core")
        with pytest.raises(ValidationError):
            cfg.agent_name = "b"  # type: ignore[misc]

    def test_forbid_extra(self) -> None:
        with pytest.raises(ValidationError):
            AgentConfig(agent_name="a", persona="core", unknown="x")  # type: ignore[call-arg]

    def test_invalid_persona_rejected(self) -> None:
        with pytest.raises(ValidationError):
            AgentConfig(agent_name="a", persona="hacker")  # type: ignore[arg-type]


class TestAgentConfigSet:
    def test_empty_set(self) -> None:
        cs = AgentConfigSet()
        assert cs.agents == []

    def test_set_with_agents(self) -> None:
        cs = AgentConfigSet(
            agents=[
                AgentConfig(agent_name="a", persona="core"),
                AgentConfig(agent_name="b", persona="infra"),
            ]
        )
        assert len(cs.agents) == 2

    def test_frozen(self) -> None:
        cs = AgentConfigSet()
        with pytest.raises(ValidationError):
            cs.agents = []  # type: ignore[misc]


# ── loader tests ──────────────────────────────────────────────────────────


class TestLoadAgentConfig:
    def test_load_valid(self) -> None:
        raw = {"agent_name": "echo", "persona": "core", "tags": ["test"]}
        cfg = load_agent_config(raw)
        assert cfg.agent_name == "echo"
        assert cfg.tags == ["test"]

    def test_load_invalid_raises(self) -> None:
        with pytest.raises(ValidationError):
            load_agent_config({"persona": "core"})  # missing agent_name


class TestLoadAgentConfigSet:
    def test_load_from_dict(self) -> None:
        raw = {
            "agents": [
                {"agent_name": "a", "persona": "core"},
                {"agent_name": "b", "persona": "docs"},
            ]
        }
        cs = load_agent_config_set(raw)
        assert len(cs.agents) == 2
        assert cs.agents[0].agent_name == "a"

    def test_load_empty(self) -> None:
        cs = load_agent_config_set({"agents": []})
        assert cs.agents == []


class TestLoadFromList:
    def test_from_list(self) -> None:
        items = [
            {"agent_name": "x", "persona": "infra"},
            {"agent_name": "y", "persona": "docs", "enabled": False},
        ]
        cs = load_agent_configs_from_list(items)
        assert len(cs.agents) == 2
        assert cs.agents[1].enabled is False

    def test_invalid_item_raises(self) -> None:
        with pytest.raises(ValidationError):
            load_agent_configs_from_list([{"agent_name": "z"}])  # missing persona
