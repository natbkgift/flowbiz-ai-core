"""Rule-based intent router.

Evaluates inbound intent strings against an ordered set of routing
rules and returns the first match.  Rules are evaluated in priority
order (descending); ties break by insertion order.
"""

from __future__ import annotations

import re

from packages.core.contracts.routing import RoutingResult, RoutingRule


class IntentRouter:
    """In-memory rule-based intent router."""

    def __init__(self) -> None:
        self._rules: list[RoutingRule] = []

    # ── mutations ──────────────────────────────────────────────────────

    def add_rule(self, rule: RoutingRule) -> None:
        """Register a routing rule."""
        if any(r.rule_id == rule.rule_id for r in self._rules):
            raise ValueError(f"Duplicate rule_id: {rule.rule_id}")
        self._rules.append(rule)

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule by id.  Returns True if found."""
        before = len(self._rules)
        self._rules = [r for r in self._rules if r.rule_id != rule_id]
        return len(self._rules) < before

    # ── queries ────────────────────────────────────────────────────────

    def list_rules(self) -> list[RoutingRule]:
        """Return all rules sorted by priority descending, then insertion order."""
        return sorted(
            self._rules,
            key=lambda r: -r.priority,
        )

    def route(self, intent: str) -> RoutingResult:
        """Evaluate *intent* against enabled rules and return the first match.

        Rules are checked in priority order (highest first).  For each
        rule the match strategy decides how to compare:

        * **keyword** — case-insensitive substring check.
        * **pattern** — ``re.search`` with the rule's value as regex.
        """
        for rule in self.list_rules():
            if not rule.enabled:
                continue
            if _matches(rule, intent):
                return RoutingResult(
                    matched=True,
                    rule_id=rule.rule_id,
                    target_persona=rule.target_persona,
                    target_agent=rule.target_agent,
                )
        return RoutingResult(matched=False)


# ── helpers ────────────────────────────────────────────────────────────────


def _matches(rule: RoutingRule, intent: str) -> bool:
    if rule.match_strategy == "keyword":
        return rule.match_value.lower() in intent.lower()
    if rule.match_strategy == "pattern":
        return re.search(rule.match_value, intent, re.IGNORECASE) is not None
    return False  # pragma: no cover
