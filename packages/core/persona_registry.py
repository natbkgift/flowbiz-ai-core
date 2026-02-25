"""In-memory persona registry for agent → persona assignments."""

from __future__ import annotations

from .contracts.persona import (
    ALL_PERSONAS,
    PersonaAssignment,
    PersonaSpec,
    PersonaType,
)


class PersonaRegistry:
    """Deterministic in-memory persona registry.

    Stores persona definitions and agent-to-persona assignments.
    """

    def __init__(self) -> None:
        self._personas: dict[PersonaType, PersonaSpec] = dict(ALL_PERSONAS)
        self._assignments: dict[str, PersonaType] = {}

    # -- persona catalogue ---------------------------------------------------

    def get_persona(self, persona: PersonaType) -> PersonaSpec:
        """Return the spec for a persona (always succeeds for valid types)."""
        return self._personas[persona]

    def list_personas(self) -> list[PersonaSpec]:
        """Return all registered persona specs in deterministic order."""
        return [self._personas[k] for k in sorted(self._personas)]

    # -- agent ↔ persona assignments -----------------------------------------

    def assign(self, agent_name: str, persona: PersonaType) -> PersonaAssignment:
        """Assign (or reassign) an agent to a persona."""
        self._assignments[agent_name] = persona
        return PersonaAssignment(agent_name=agent_name, persona=persona)

    def get_assignment(self, agent_name: str) -> PersonaAssignment | None:
        """Look up the persona for an agent; returns None if unassigned."""
        persona = self._assignments.get(agent_name)
        if persona is None:
            return None
        return PersonaAssignment(agent_name=agent_name, persona=persona)

    def list_assignments(self) -> list[PersonaAssignment]:
        """Return all assignments in deterministic sorted order."""
        return [
            PersonaAssignment(agent_name=name, persona=p)
            for name, p in sorted(self._assignments.items())
        ]

    def agents_for_persona(self, persona: PersonaType) -> list[str]:
        """Return sorted list of agent names assigned to a persona."""
        return sorted(
            name for name, p in self._assignments.items() if p == persona
        )

    def remove_assignment(self, agent_name: str) -> bool:
        """Remove an agent's persona assignment. Returns True if it existed."""
        return self._assignments.pop(agent_name, None) is not None
