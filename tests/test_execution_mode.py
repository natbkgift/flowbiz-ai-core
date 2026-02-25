"""Tests for execution mode (deterministic toggle)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.execution_mode import (
    CREATIVE_MODE,
    DETERMINISTIC_MODE,
    ExecutionMode,
    resolve_mode,
)


class TestExecutionModeContract:
    def test_defaults(self) -> None:
        m = ExecutionMode()
        assert m.deterministic is True
        assert m.temperature == 0.0
        assert m.seed is None

    def test_frozen(self) -> None:
        m = ExecutionMode()
        with pytest.raises(ValidationError):
            m.deterministic = False  # type: ignore[misc]

    def test_forbid_extra(self) -> None:
        with pytest.raises(ValidationError):
            ExecutionMode(extra_field="bad")  # type: ignore[call-arg]


class TestPrebuiltModes:
    def test_deterministic_mode(self) -> None:
        assert DETERMINISTIC_MODE.deterministic is True
        assert DETERMINISTIC_MODE.temperature == 0.0
        assert DETERMINISTIC_MODE.seed == 42

    def test_creative_mode(self) -> None:
        assert CREATIVE_MODE.deterministic is False
        assert CREATIVE_MODE.temperature == 0.7


class TestResolveMode:
    def test_override_wins(self) -> None:
        custom = ExecutionMode(deterministic=False, temperature=0.5)
        result = resolve_mode(override=custom)
        assert result is custom

    def test_default_deterministic(self) -> None:
        result = resolve_mode(default_deterministic=True)
        assert result is DETERMINISTIC_MODE

    def test_default_creative(self) -> None:
        result = resolve_mode(default_deterministic=False)
        assert result is CREATIVE_MODE

    def test_none_override_uses_default(self) -> None:
        result = resolve_mode(override=None)
        assert result.deterministic is True
