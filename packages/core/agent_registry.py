"""Agent Registry v2 - Interface and In-Memory Implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Protocol

from .contracts.agent_registry import AgentRegistration, AgentSpec


class AgentRegistryProtocol(Protocol):
    """Protocol defining Agent Registry operations."""

    def register(self, spec: AgentSpec) -> AgentRegistration:
        """Register an agent spec in the registry."""
        ...

    def list_all(self, include_disabled: bool = False) -> list[AgentRegistration]:
        """List all agent registrations sorted by agent_name."""
        ...

    def get(self, agent_name: str) -> AgentRegistration | None:
        """Get an agent registration by name."""
        ...

    def set_enabled(self, agent_name: str, enabled: bool) -> AgentRegistration:
        """Enable or disable an agent registration."""
        ...

    def remove(self, agent_name: str) -> None:
        """Remove an agent registration by name."""
        ...


class AgentRegistryABC(ABC):
    """Abstract base class for Agent Registry implementations."""

    @abstractmethod
    def register(self, spec: AgentSpec) -> AgentRegistration:
        """Register an agent spec in the registry."""
        ...

    @abstractmethod
    def list_all(self, include_disabled: bool = False) -> list[AgentRegistration]:
        """List all agent registrations sorted by agent_name."""
        ...

    @abstractmethod
    def get(self, agent_name: str) -> AgentRegistration | None:
        """Get an agent registration by name."""
        ...

    @abstractmethod
    def set_enabled(self, agent_name: str, enabled: bool) -> AgentRegistration:
        """Enable or disable an agent registration."""
        ...

    @abstractmethod
    def remove(self, agent_name: str) -> None:
        """Remove an agent registration by name."""
        ...


class InMemoryAgentRegistry(AgentRegistryABC):
    """In-memory Agent Registry v2 implementation with deterministic behavior."""

    def __init__(self) -> None:
        self._agents: dict[str, AgentRegistration] = {}

    def register(self, spec: AgentSpec) -> AgentRegistration:
        agent_name = spec.agent_name
        existing = self._agents.get(agent_name)

        if existing is None:
            created_at = datetime.now(timezone.utc).isoformat()
            registration = AgentRegistration(
                spec=spec,
                enabled=True,
                created_at=created_at,
            )
            self._agents[agent_name] = registration
            return registration

        if existing.spec == spec:
            return existing

        if existing.spec.version == spec.version:
            version_str = (
                f"'{spec.version}'"
                if spec.version is not None
                else "None (unversioned)"
            )
            raise ValueError(
                f"Cannot register agent '{agent_name}' with version {version_str}: "
                "a different specification already exists with this version. "
                "Update the version to register a new specification."
            )

        created_at = datetime.now(timezone.utc).isoformat()
        updated = AgentRegistration(
            spec=spec,
            enabled=existing.enabled,
            created_at=created_at,
        )
        self._agents[agent_name] = updated
        return updated

    def list_all(self, include_disabled: bool = False) -> list[AgentRegistration]:
        agents = list(self._agents.values())
        if not include_disabled:
            agents = [registration for registration in agents if registration.enabled]

        return sorted(agents, key=lambda registration: registration.spec.agent_name)

    def get(self, agent_name: str) -> AgentRegistration | None:
        return self._agents.get(agent_name)

    def set_enabled(self, agent_name: str, enabled: bool) -> AgentRegistration:
        existing = self._agents.get(agent_name)
        if existing is None:
            raise KeyError(f"Agent '{agent_name}' is not registered")

        if existing.enabled == enabled:
            return existing

        updated = AgentRegistration(
            spec=existing.spec,
            enabled=enabled,
            created_at=existing.created_at,
        )
        self._agents[agent_name] = updated
        return updated

    def remove(self, agent_name: str) -> None:
        self._agents.pop(agent_name, None)
