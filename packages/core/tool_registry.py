"""Tool Registry v2 - Interface and In-Memory Implementation.

This module provides the Tool Registry v2 functionality, including:
- A protocol/interface defining registry operations
- An in-memory implementation for deterministic, testable behavior

The registry supports:
- Registering tools with their specifications
- Listing all registered tools (with optional filtering)
- Getting individual tool registrations
- Enabling/disabling tools
- Removing tools

All operations are deterministic and produce stable, sorted results.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Protocol

from .contracts.tool_registry import ToolRegistration, ToolSpec


class ToolRegistryProtocol(Protocol):
    """Protocol defining the Tool Registry interface.

    This protocol establishes the contract for tool registry implementations.
    All implementations must provide these methods with the specified behavior.
    """

    def register(self, spec: ToolSpec) -> ToolRegistration:
        """Register a tool with the given specification.

        Behavior:
        - If tool_name does not exist: creates a new registration
        - If tool_name exists with same spec: returns existing registration unchanged
        - If tool_name exists with different version: overwrites with new registration
        - If tool_name exists with same version but different spec: raises ValueError

        Args:
            spec: The tool specification to register

        Returns:
            The tool registration (new or existing)

        Raises:
            ValueError: If attempting to register a tool with the same name and version
                       but different specification
        """
        ...

    def list_all(self, include_disabled: bool = False) -> list[ToolRegistration]:
        """List all registered tools.

        Behavior:
        - Returns tools sorted by tool_name (ascending) for deterministic ordering
        - By default, excludes disabled tools
        - When include_disabled=True, includes all tools regardless of status

        Args:
            include_disabled: Whether to include disabled tools (default: False)

        Returns:
            List of tool registrations, sorted by tool_name
        """
        ...

    def get(self, tool_name: str) -> ToolRegistration | None:
        """Get a specific tool registration by name.

        Args:
            tool_name: The unique name of the tool

        Returns:
            The tool registration if found, None otherwise
        """
        ...

    def set_enabled(self, tool_name: str, enabled: bool) -> ToolRegistration:
        """Enable or disable a tool.

        Args:
            tool_name: The unique name of the tool
            enabled: Whether to enable (True) or disable (False) the tool

        Returns:
            The updated tool registration

        Raises:
            KeyError: If the tool_name is not registered
        """
        ...

    def remove(self, tool_name: str) -> None:
        """Remove a tool from the registry.

        This operation is safe and deterministic. If the tool does not exist,
        the operation completes without error (idempotent behavior).

        Args:
            tool_name: The unique name of the tool to remove
        """
        ...


class ToolRegistryABC(ABC):
    """Abstract base class for Tool Registry implementations.

    This ABC provides the same interface as ToolRegistryProtocol but can be
    used with inheritance-based patterns if preferred over duck typing.
    """

    @abstractmethod
    def register(self, spec: ToolSpec) -> ToolRegistration:
        """Register a tool with the given specification."""
        ...

    @abstractmethod
    def list_all(self, include_disabled: bool = False) -> list[ToolRegistration]:
        """List all registered tools."""
        ...

    @abstractmethod
    def get(self, tool_name: str) -> ToolRegistration | None:
        """Get a specific tool registration by name."""
        ...

    @abstractmethod
    def set_enabled(self, tool_name: str, enabled: bool) -> ToolRegistration:
        """Enable or disable a tool."""
        ...

    @abstractmethod
    def remove(self, tool_name: str) -> None:
        """Remove a tool from the registry."""
        ...


class InMemoryToolRegistry(ToolRegistryABC):
    """In-memory implementation of Tool Registry.

    This implementation stores tool registrations in a dictionary keyed by tool_name.
    It provides deterministic, testable behavior with no external dependencies.

    Characteristics:
    - No global state (instance-based)
    - No side effects outside the instance
    - Stable, sorted ordering in list_all()
    - Thread-safe for single-threaded use (not designed for concurrent access)
    - No persistence (data lost when instance is destroyed)

    Usage:
        registry = InMemoryToolRegistry()
        spec = ToolSpec(
            tool_name="example",
            input_schema={},
            output_schema={}
        )
        registration = registry.register(spec)
    """

    def __init__(self) -> None:
        """Initialize an empty in-memory tool registry."""
        self._tools: dict[str, ToolRegistration] = {}

    def register(self, spec: ToolSpec) -> ToolRegistration:
        """Register a tool with the given specification.

        Registration rules:
        1. If tool_name is new: create new registration with enabled=True
        2. If tool_name exists with identical spec: return existing registration
        3. If tool_name exists with different version: overwrite with new registration
        4. If tool_name exists with same version but different spec: raise ValueError

        Args:
            spec: The tool specification to register

        Returns:
            The tool registration (new or existing)

        Raises:
            ValueError: If attempting to register a tool with the same name and version
                       but different specification
        """
        tool_name = spec.tool_name
        existing = self._tools.get(tool_name)

        if existing is None:
            # New tool: create registration with current timestamp
            created_at = datetime.now(timezone.utc).isoformat()
            registration = ToolRegistration(
                spec=spec, enabled=True, created_at=created_at
            )
            self._tools[tool_name] = registration
            return registration

        # Tool exists: check if we can overwrite
        if existing.spec == spec:
            # Identical spec: return existing unchanged
            return existing

        # Different spec: check version
        if existing.spec.version == spec.version:
            # Same version, different spec: forbidden
            raise ValueError(
                f"Cannot register tool '{tool_name}' with version '{spec.version}': "
                f"a different specification already exists with this version. "
                f"Update the version to register a new specification."
            )

        # Different version: overwrite with new registration
        # Preserve enabled state from existing registration
        created_at = datetime.now(timezone.utc).isoformat()
        registration = ToolRegistration(
            spec=spec, enabled=existing.enabled, created_at=created_at
        )
        self._tools[tool_name] = registration
        return registration

    def list_all(self, include_disabled: bool = False) -> list[ToolRegistration]:
        """List all registered tools.

        Returns tools sorted by tool_name (ascending) for deterministic ordering.

        Args:
            include_disabled: Whether to include disabled tools (default: False)

        Returns:
            List of tool registrations, sorted by tool_name
        """
        tools = list(self._tools.values())

        if not include_disabled:
            tools = [t for t in tools if t.enabled]

        # Sort by tool_name for stable, deterministic ordering
        return sorted(tools, key=lambda t: t.spec.tool_name)

    def get(self, tool_name: str) -> ToolRegistration | None:
        """Get a specific tool registration by name.

        Args:
            tool_name: The unique name of the tool

        Returns:
            The tool registration if found, None otherwise
        """
        return self._tools.get(tool_name)

    def set_enabled(self, tool_name: str, enabled: bool) -> ToolRegistration:
        """Enable or disable a tool.

        Creates a new ToolRegistration with the updated enabled state.
        Due to contract immutability, we cannot modify existing registrations.

        Args:
            tool_name: The unique name of the tool
            enabled: Whether to enable (True) or disable (False) the tool

        Returns:
            The updated tool registration

        Raises:
            KeyError: If the tool_name is not registered
        """
        existing = self._tools.get(tool_name)
        if existing is None:
            raise KeyError(f"Tool '{tool_name}' is not registered")

        if existing.enabled == enabled:
            # Already in desired state: return unchanged
            return existing

        # Create new registration with updated enabled state
        # Preserve spec and created_at from existing registration
        updated = ToolRegistration(
            spec=existing.spec, enabled=enabled, created_at=existing.created_at
        )
        self._tools[tool_name] = updated
        return updated

    def remove(self, tool_name: str) -> None:
        """Remove a tool from the registry.

        This operation is idempotent: removing a non-existent tool succeeds silently.

        Args:
            tool_name: The unique name of the tool to remove
        """
        self._tools.pop(tool_name, None)
