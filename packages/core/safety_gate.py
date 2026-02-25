"""Safety gate hook abstraction and default implementation."""

from __future__ import annotations

from typing import Protocol

from .contracts.safety import SafetyDecision, SafetyGateInput


class SafetyGateProtocol(Protocol):
    """Protocol for safety pre-check implementations."""

    def check(self, payload: SafetyGateInput) -> SafetyDecision:
        """Evaluate whether runtime execution should proceed."""
        ...


class AllowAllSafetyGate:
    """Default safety gate that always allows execution."""

    def check(self, payload: SafetyGateInput) -> SafetyDecision:
        return SafetyDecision(decision="allow")
