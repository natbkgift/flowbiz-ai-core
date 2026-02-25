"""Tests for PR-028 optional safety gate hook."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.contracts.safety import SafetyDecision, SafetyGateInput
from packages.core.safety_gate import AllowAllSafetyGate


def test_safety_contracts_are_immutable() -> None:
    payload = SafetyGateInput(trace_id="t-1", agent="echo", text="hello")
    decision = SafetyDecision(decision="allow")

    with pytest.raises((ValidationError, AttributeError)):
        payload.text = "changed"  # type: ignore[misc]

    with pytest.raises((ValidationError, AttributeError)):
        decision.decision = "deny"  # type: ignore[misc]


def test_allow_all_safety_gate_allows() -> None:
    gate = AllowAllSafetyGate()
    result = gate.check(SafetyGateInput(trace_id="t-2", agent="echo", text="ok"))

    assert result.decision == "allow"
    assert result.reason is None
