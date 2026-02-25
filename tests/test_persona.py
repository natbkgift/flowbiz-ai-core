"""Tests for persona contracts and PersonaRegistry."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.contracts.persona import (
    ALL_PERSONAS,
    CORE_PERSONA,
    DOCS_PERSONA,
    INFRA_PERSONA,
    PersonaAssignment,
    PersonaSpec,
)
from packages.core.persona_registry import PersonaRegistry


# ── contract immutability ─────────────────────────────────────────────────


class TestPersonaContracts:
    def test_persona_spec_frozen(self) -> None:
        with pytest.raises(ValidationError):
            PersonaSpec(persona="core", display_name="Core", extra_field="bad")  # type: ignore[call-arg]

    def test_persona_spec_immutable(self) -> None:
        spec = CORE_PERSONA
        with pytest.raises(ValidationError):
            spec.persona = "docs"  # type: ignore[misc]

    def test_persona_assignment_frozen(self) -> None:
        a = PersonaAssignment(agent_name="echo", persona="core")
        with pytest.raises(ValidationError):
            a.persona = "infra"  # type: ignore[misc]

    def test_persona_assignment_rejects_invalid(self) -> None:
        with pytest.raises(ValidationError):
            PersonaAssignment(agent_name="x", persona="invalid")  # type: ignore[arg-type]

    def test_all_personas_contains_three(self) -> None:
        assert set(ALL_PERSONAS.keys()) == {"core", "infra", "docs"}

    def test_canonical_specs(self) -> None:
        assert CORE_PERSONA.persona == "core"
        assert INFRA_PERSONA.persona == "infra"
        assert DOCS_PERSONA.persona == "docs"


# ── registry ──────────────────────────────────────────────────────────────


class TestPersonaRegistry:
    def test_list_personas_returns_all(self) -> None:
        reg = PersonaRegistry()
        specs = reg.list_personas()
        assert len(specs) == 3
        assert [s.persona for s in specs] == ["core", "docs", "infra"]

    def test_get_persona(self) -> None:
        reg = PersonaRegistry()
        assert reg.get_persona("core") == CORE_PERSONA

    def test_assign_and_get(self) -> None:
        reg = PersonaRegistry()
        assignment = reg.assign("echo", "core")
        assert assignment.agent_name == "echo"
        assert assignment.persona == "core"
        assert reg.get_assignment("echo") == assignment

    def test_get_unassigned_returns_none(self) -> None:
        reg = PersonaRegistry()
        assert reg.get_assignment("nonexistent") is None

    def test_reassign(self) -> None:
        reg = PersonaRegistry()
        reg.assign("echo", "core")
        reg.assign("echo", "infra")
        a = reg.get_assignment("echo")
        assert a is not None
        assert a.persona == "infra"

    def test_list_assignments_sorted(self) -> None:
        reg = PersonaRegistry()
        reg.assign("zeta", "docs")
        reg.assign("alpha", "core")
        assignments = reg.list_assignments()
        assert [a.agent_name for a in assignments] == ["alpha", "zeta"]

    def test_agents_for_persona(self) -> None:
        reg = PersonaRegistry()
        reg.assign("a1", "core")
        reg.assign("a2", "core")
        reg.assign("a3", "infra")
        assert reg.agents_for_persona("core") == ["a1", "a2"]
        assert reg.agents_for_persona("infra") == ["a3"]
        assert reg.agents_for_persona("docs") == []

    def test_remove_assignment(self) -> None:
        reg = PersonaRegistry()
        reg.assign("echo", "core")
        assert reg.remove_assignment("echo") is True
        assert reg.get_assignment("echo") is None

    def test_remove_nonexistent_returns_false(self) -> None:
        reg = PersonaRegistry()
        assert reg.remove_assignment("ghost") is False
