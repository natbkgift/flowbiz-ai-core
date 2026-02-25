"""Tests for Agent Registry v2 contracts and implementation."""

from __future__ import annotations

import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from packages.core.agent_registry import InMemoryAgentRegistry
from packages.core.contracts.agent_registry import (
    AgentRegistration,
    AgentRegistrySnapshot,
    AgentSpec,
)


def test_agent_spec_round_trip_and_immutability() -> None:
    spec = AgentSpec(
        agent_name="echo",
        version="1.0.0",
        description="Echo agent",
        tags=["default"],
    )

    dumped = spec.model_dump()
    loaded = AgentSpec.model_validate(dumped)
    assert loaded == spec
    assert json.loads(json.dumps(dumped)) == dumped

    with pytest.raises((ValidationError, AttributeError)):
        spec.agent_name = "changed"  # type: ignore[misc]


def test_agent_registration_and_snapshot_contracts() -> None:
    spec = AgentSpec(agent_name="echo")
    registration = AgentRegistration(spec=spec, enabled=True)
    snapshot = AgentRegistrySnapshot(agents=[registration])

    assert snapshot.agents[0].spec.agent_name == "echo"

    with pytest.raises((ValidationError, AttributeError)):
        snapshot.agents = []  # type: ignore[misc]


def test_register_get_and_sorted_list() -> None:
    registry = InMemoryAgentRegistry()
    registry.register(AgentSpec(agent_name="bravo"))
    registry.register(AgentSpec(agent_name="alpha"))

    registrations = registry.list_all()
    assert [item.spec.agent_name for item in registrations] == ["alpha", "bravo"]

    retrieved = registry.get("alpha")
    assert retrieved is not None
    assert retrieved.spec.agent_name == "alpha"
    assert retrieved.created_at is not None
    datetime.fromisoformat(retrieved.created_at)


def test_register_same_version_different_spec_raises_value_error() -> None:
    registry = InMemoryAgentRegistry()
    registry.register(AgentSpec(agent_name="echo", version="1.0.0", tags=["a"]))

    with pytest.raises(ValueError):
        registry.register(AgentSpec(agent_name="echo", version="1.0.0", tags=["b"]))


def test_enable_disable_and_include_disabled_behavior() -> None:
    registry = InMemoryAgentRegistry()
    registry.register(AgentSpec(agent_name="echo"))
    registry.set_enabled("echo", False)

    assert registry.list_all() == []
    with_disabled = registry.list_all(include_disabled=True)
    assert len(with_disabled) == 1
    assert with_disabled[0].enabled is False

    registry.set_enabled("echo", True)
    enabled = registry.get("echo")
    assert enabled is not None
    assert enabled.enabled is True


def test_remove_is_idempotent() -> None:
    registry = InMemoryAgentRegistry()
    registry.register(AgentSpec(agent_name="echo"))

    registry.remove("echo")
    registry.remove("echo")

    assert registry.get("echo") is None
