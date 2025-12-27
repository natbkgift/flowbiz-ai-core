"""Tests for Tool Registry v2.

This test suite validates:
- Contract immutability
- Round-trip serialization
- Registry registration logic
- Enable/disable functionality
- Stable sorting and deterministic behavior
- Error handling for edge cases
"""

import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from packages.core.contracts.tool_registry import (
    ToolRegistration,
    ToolRegistrySnapshot,
    ToolSpec,
)
from packages.core.tool_registry import InMemoryToolRegistry


# Contract Tests
class TestToolSpecContract:
    """Tests for ToolSpec contract schema."""

    def test_minimal_spec(self):
        """Test creating a minimal ToolSpec with required fields only."""
        spec = ToolSpec(
            tool_name="example",
            input_schema={"field": "string"},
            output_schema={"result": "number"},
        )
        assert spec.tool_name == "example"
        assert spec.version is None
        assert spec.description is None
        assert spec.input_schema == {"field": "string"}
        assert spec.output_schema == {"result": "number"}
        assert spec.tags == []

    def test_full_spec(self):
        """Test creating a ToolSpec with all optional fields."""
        spec = ToolSpec(
            tool_name="weather",
            version="1.0.0",
            description="Look up weather data",
            input_schema={"city": "string"},
            output_schema={"temp": "number", "humidity": "number"},
            tags=["weather", "api", "data"],
        )
        assert spec.tool_name == "weather"
        assert spec.version == "1.0.0"
        assert spec.description == "Look up weather data"
        assert spec.tags == ["weather", "api", "data"]

    def test_immutability(self):
        """Test that ToolSpec is immutable (frozen)."""
        spec = ToolSpec(
            tool_name="example",
            input_schema={},
            output_schema={},
        )
        with pytest.raises((ValidationError, AttributeError)):
            spec.tool_name = "modified"  # type: ignore

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError):
            ToolSpec(
                tool_name="example",
                input_schema={},
                output_schema={},
                extra_field="not_allowed",  # type: ignore
            )

    def test_round_trip_serialization(self):
        """Test model_dump and model_validate round trip."""
        spec = ToolSpec(
            tool_name="example",
            version="1.0.0",
            description="test tool",
            input_schema={"a": "string"},
            output_schema={"b": "number"},
            tags=["test"],
        )
        dumped = spec.model_dump()
        loaded = ToolSpec.model_validate(dumped)
        assert loaded == spec
        assert json.loads(json.dumps(dumped)) == dumped

    def test_json_round_trip(self):
        """Test model_dump_json and model_validate_json round trip."""
        spec = ToolSpec(
            tool_name="example",
            version="2.0.0",
            input_schema={"x": "number"},
            output_schema={"y": "string"},
        )
        json_str = spec.model_dump_json()
        loaded = ToolSpec.model_validate_json(json_str)
        assert loaded == spec


class TestToolRegistrationContract:
    """Tests for ToolRegistration contract schema."""

    def test_minimal_registration(self):
        """Test creating a minimal ToolRegistration."""
        spec = ToolSpec(tool_name="example", input_schema={}, output_schema={})
        reg = ToolRegistration(spec=spec)
        assert reg.spec == spec
        assert reg.enabled is True
        assert reg.created_at is None

    def test_full_registration(self):
        """Test creating a ToolRegistration with all fields."""
        spec = ToolSpec(tool_name="example", input_schema={}, output_schema={})
        reg = ToolRegistration(
            spec=spec, enabled=False, created_at="2025-12-27T14:00:00Z"
        )
        assert reg.spec == spec
        assert reg.enabled is False
        assert reg.created_at == "2025-12-27T14:00:00Z"

    def test_immutability(self):
        """Test that ToolRegistration is immutable."""
        spec = ToolSpec(tool_name="example", input_schema={}, output_schema={})
        reg = ToolRegistration(spec=spec)
        with pytest.raises((ValidationError, AttributeError)):
            reg.enabled = False  # type: ignore

    def test_round_trip_serialization(self):
        """Test serialization round trip for ToolRegistration."""
        spec = ToolSpec(
            tool_name="example",
            version="1.0.0",
            input_schema={"a": "string"},
            output_schema={"b": "number"},
        )
        reg = ToolRegistration(spec=spec, enabled=False, created_at="2025-12-27T14:00:00Z")
        dumped = reg.model_dump()
        loaded = ToolRegistration.model_validate(dumped)
        assert loaded == reg


class TestToolRegistrySnapshotContract:
    """Tests for ToolRegistrySnapshot contract schema."""

    def test_empty_snapshot(self):
        """Test creating an empty snapshot."""
        snapshot = ToolRegistrySnapshot(tools=[])
        assert snapshot.tools == []

    def test_snapshot_with_tools(self):
        """Test creating a snapshot with multiple tools."""
        spec1 = ToolSpec(tool_name="tool1", input_schema={}, output_schema={})
        spec2 = ToolSpec(tool_name="tool2", input_schema={}, output_schema={})
        reg1 = ToolRegistration(spec=spec1)
        reg2 = ToolRegistration(spec=spec2)
        snapshot = ToolRegistrySnapshot(tools=[reg1, reg2])
        assert len(snapshot.tools) == 2
        assert snapshot.tools[0].spec.tool_name == "tool1"
        assert snapshot.tools[1].spec.tool_name == "tool2"

    def test_immutability(self):
        """Test that ToolRegistrySnapshot is immutable."""
        snapshot = ToolRegistrySnapshot(tools=[])
        with pytest.raises((ValidationError, AttributeError)):
            snapshot.tools = []  # type: ignore


# Registry Implementation Tests
class TestInMemoryToolRegistry:
    """Tests for InMemoryToolRegistry implementation."""

    def test_register_new_tool(self):
        """Test registering a new tool."""
        registry = InMemoryToolRegistry()
        spec = ToolSpec(
            tool_name="example",
            version="1.0.0",
            input_schema={},
            output_schema={},
        )
        reg = registry.register(spec)

        assert reg.spec == spec
        assert reg.enabled is True
        assert reg.created_at is not None
        # Verify created_at is valid ISO8601
        datetime.fromisoformat(reg.created_at)

    def test_register_then_get(self):
        """Test that registered tool can be retrieved."""
        registry = InMemoryToolRegistry()
        spec = ToolSpec(tool_name="example", input_schema={}, output_schema={})
        registered = registry.register(spec)
        retrieved = registry.get("example")

        assert retrieved is not None
        assert retrieved == registered

    def test_register_identical_spec_returns_existing(self):
        """Test that registering identical spec returns existing registration."""
        registry = InMemoryToolRegistry()
        spec = ToolSpec(
            tool_name="example",
            version="1.0.0",
            input_schema={"a": "string"},
            output_schema={"b": "number"},
        )
        reg1 = registry.register(spec)
        reg2 = registry.register(spec)

        assert reg1 == reg2

    def test_register_different_version_overwrites(self):
        """Test that registering with different version overwrites."""
        registry = InMemoryToolRegistry()
        spec_v1 = ToolSpec(
            tool_name="example",
            version="1.0.0",
            input_schema={},
            output_schema={},
        )
        spec_v2 = ToolSpec(
            tool_name="example",
            version="2.0.0",
            input_schema={"new_field": "string"},
            output_schema={},
        )
        reg1 = registry.register(spec_v1)
        reg2 = registry.register(spec_v2)

        assert reg1.spec.version == "1.0.0"
        assert reg2.spec.version == "2.0.0"
        # Verify only v2 remains
        retrieved = registry.get("example")
        assert retrieved is not None
        assert retrieved.spec.version == "2.0.0"

    def test_register_same_version_different_spec_raises_error(self):
        """Test that registering same version with different spec raises ValueError."""
        registry = InMemoryToolRegistry()
        spec_v1 = ToolSpec(
            tool_name="example",
            version="1.0.0",
            input_schema={"field1": "string"},
            output_schema={},
        )
        spec_v1_modified = ToolSpec(
            tool_name="example",
            version="1.0.0",  # Same version
            input_schema={"field2": "number"},  # Different schema
            output_schema={},
        )
        registry.register(spec_v1)

        with pytest.raises(ValueError) as exc_info:
            registry.register(spec_v1_modified)
        assert "version" in str(exc_info.value).lower()

    def test_list_all_empty(self):
        """Test listing from empty registry."""
        registry = InMemoryToolRegistry()
        tools = registry.list_all()
        assert tools == []

    def test_list_all_returns_sorted(self):
        """Test that list_all returns tools sorted by tool_name."""
        registry = InMemoryToolRegistry()
        # Register in non-alphabetical order
        spec_c = ToolSpec(tool_name="charlie", input_schema={}, output_schema={})
        spec_a = ToolSpec(tool_name="alpha", input_schema={}, output_schema={})
        spec_b = ToolSpec(tool_name="bravo", input_schema={}, output_schema={})

        registry.register(spec_c)
        registry.register(spec_a)
        registry.register(spec_b)

        tools = registry.list_all()
        assert len(tools) == 3
        assert tools[0].spec.tool_name == "alpha"
        assert tools[1].spec.tool_name == "bravo"
        assert tools[2].spec.tool_name == "charlie"

    def test_list_all_excludes_disabled_by_default(self):
        """Test that list_all excludes disabled tools by default."""
        registry = InMemoryToolRegistry()
        spec1 = ToolSpec(tool_name="enabled", input_schema={}, output_schema={})
        spec2 = ToolSpec(tool_name="disabled", input_schema={}, output_schema={})

        registry.register(spec1)
        registry.register(spec2)
        registry.set_enabled("disabled", enabled=False)

        tools = registry.list_all()
        assert len(tools) == 1
        assert tools[0].spec.tool_name == "enabled"

    def test_list_all_includes_disabled_when_requested(self):
        """Test that list_all includes disabled tools when include_disabled=True."""
        registry = InMemoryToolRegistry()
        spec1 = ToolSpec(tool_name="enabled", input_schema={}, output_schema={})
        spec2 = ToolSpec(tool_name="disabled", input_schema={}, output_schema={})

        registry.register(spec1)
        registry.register(spec2)
        registry.set_enabled("disabled", enabled=False)

        tools = registry.list_all(include_disabled=True)
        assert len(tools) == 2
        # Still sorted
        assert tools[0].spec.tool_name == "disabled"
        assert tools[1].spec.tool_name == "enabled"

    def test_get_unknown_tool_returns_none(self):
        """Test that getting unknown tool returns None."""
        registry = InMemoryToolRegistry()
        result = registry.get("unknown")
        assert result is None

    def test_set_enabled_disables_tool(self):
        """Test disabling a tool."""
        registry = InMemoryToolRegistry()
        spec = ToolSpec(tool_name="example", input_schema={}, output_schema={})
        registry.register(spec)

        updated = registry.set_enabled("example", enabled=False)
        assert updated.enabled is False

        # Verify persisted
        retrieved = registry.get("example")
        assert retrieved is not None
        assert retrieved.enabled is False

    def test_set_enabled_enables_tool(self):
        """Test re-enabling a disabled tool."""
        registry = InMemoryToolRegistry()
        spec = ToolSpec(tool_name="example", input_schema={}, output_schema={})
        registry.register(spec)
        registry.set_enabled("example", enabled=False)

        updated = registry.set_enabled("example", enabled=True)
        assert updated.enabled is True

        # Verify persisted
        retrieved = registry.get("example")
        assert retrieved is not None
        assert retrieved.enabled is True

    def test_set_enabled_unknown_tool_raises_error(self):
        """Test that set_enabled on unknown tool raises KeyError."""
        registry = InMemoryToolRegistry()

        with pytest.raises(KeyError) as exc_info:
            registry.set_enabled("unknown", enabled=False)
        assert "unknown" in str(exc_info.value).lower()

    def test_set_enabled_idempotent(self):
        """Test that set_enabled with same state is idempotent."""
        registry = InMemoryToolRegistry()
        spec = ToolSpec(tool_name="example", input_schema={}, output_schema={})
        reg1 = registry.register(spec)

        # Set to True (already True)
        reg2 = registry.set_enabled("example", enabled=True)
        assert reg1 == reg2

        # Set to False
        reg3 = registry.set_enabled("example", enabled=False)
        assert reg3.enabled is False

        # Set to False again (idempotent)
        reg4 = registry.set_enabled("example", enabled=False)
        assert reg3 == reg4

    def test_remove_existing_tool(self):
        """Test removing an existing tool."""
        registry = InMemoryToolRegistry()
        spec = ToolSpec(tool_name="example", input_schema={}, output_schema={})
        registry.register(spec)

        assert registry.get("example") is not None
        registry.remove("example")
        assert registry.get("example") is None

    def test_remove_unknown_tool_succeeds(self):
        """Test that removing unknown tool succeeds silently (idempotent)."""
        registry = InMemoryToolRegistry()
        # Should not raise
        registry.remove("unknown")

    def test_remove_is_idempotent(self):
        """Test that remove can be called multiple times safely."""
        registry = InMemoryToolRegistry()
        spec = ToolSpec(tool_name="example", input_schema={}, output_schema={})
        registry.register(spec)

        registry.remove("example")
        registry.remove("example")  # Second remove should succeed
        assert registry.get("example") is None

    def test_multiple_registries_are_independent(self):
        """Test that multiple registry instances don't share state."""
        registry1 = InMemoryToolRegistry()
        registry2 = InMemoryToolRegistry()

        spec = ToolSpec(tool_name="example", input_schema={}, output_schema={})
        registry1.register(spec)

        assert registry1.get("example") is not None
        assert registry2.get("example") is None

    def test_version_overwrite_preserves_enabled_state(self):
        """Test that version overwrite preserves the enabled state."""
        registry = InMemoryToolRegistry()
        spec_v1 = ToolSpec(
            tool_name="example",
            version="1.0.0",
            input_schema={},
            output_schema={},
        )
        registry.register(spec_v1)
        registry.set_enabled("example", enabled=False)

        spec_v2 = ToolSpec(
            tool_name="example",
            version="2.0.0",
            input_schema={},
            output_schema={},
        )
        registry.register(spec_v2)

        # Verify enabled state was preserved
        retrieved = registry.get("example")
        assert retrieved is not None
        assert retrieved.spec.version == "2.0.0"
        assert retrieved.enabled is False


class TestIntegrationScenarios:
    """Integration tests for common usage scenarios."""

    def test_full_lifecycle(self):
        """Test a complete tool lifecycle: register, disable, re-enable, remove."""
        registry = InMemoryToolRegistry()

        # Register
        spec = ToolSpec(
            tool_name="lifecycle_tool",
            version="1.0.0",
            description="Test tool for lifecycle",
            input_schema={"input": "string"},
            output_schema={"output": "string"},
            tags=["test"],
        )
        reg = registry.register(spec)
        assert reg.enabled is True

        # List (should appear)
        tools = registry.list_all()
        assert len(tools) == 1

        # Disable
        registry.set_enabled("lifecycle_tool", enabled=False)
        tools = registry.list_all()
        assert len(tools) == 0  # Excluded by default
        tools = registry.list_all(include_disabled=True)
        assert len(tools) == 1

        # Re-enable
        registry.set_enabled("lifecycle_tool", enabled=True)
        tools = registry.list_all()
        assert len(tools) == 1

        # Remove
        registry.remove("lifecycle_tool")
        assert registry.get("lifecycle_tool") is None

    def test_multiple_tools_sorting(self):
        """Test that multiple tools are always returned in sorted order."""
        registry = InMemoryToolRegistry()

        tool_names = ["zeta", "alpha", "beta", "gamma", "delta"]
        for name in tool_names:
            spec = ToolSpec(tool_name=name, input_schema={}, output_schema={})
            registry.register(spec)

        tools = registry.list_all()
        sorted_names = [t.spec.tool_name for t in tools]
        assert sorted_names == sorted(tool_names)

    def test_snapshot_creation(self):
        """Test creating a snapshot of registry state."""
        registry = InMemoryToolRegistry()

        spec1 = ToolSpec(tool_name="tool1", input_schema={}, output_schema={})
        spec2 = ToolSpec(tool_name="tool2", input_schema={}, output_schema={})
        registry.register(spec1)
        registry.register(spec2)

        tools = registry.list_all(include_disabled=True)
        snapshot = ToolRegistrySnapshot(tools=tools)

        assert len(snapshot.tools) == 2
        # Verify snapshot can be serialized
        json_str = snapshot.model_dump_json()
        loaded = ToolRegistrySnapshot.model_validate_json(json_str)
        assert loaded == snapshot
