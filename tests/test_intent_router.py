"""Tests for routing rule contracts and IntentRouter."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.contracts.routing import RoutingResult, RoutingRule
from packages.core.intent_router import IntentRouter


# ── contract immutability ─────────────────────────────────────────────────

class TestRoutingContracts:
    def test_routing_rule_frozen(self) -> None:
        r = RoutingRule(
            rule_id="r1",
            match_strategy="keyword",
            match_value="deploy",
            target_persona="infra",
        )
        with pytest.raises(ValidationError):
            r.rule_id = "r2"  # type: ignore[misc]

    def test_routing_rule_rejects_extra(self) -> None:
        with pytest.raises(ValidationError):
            RoutingRule(
                rule_id="r1",
                match_strategy="keyword",
                match_value="x",
                target_persona="core",
                extra_field="bad",  # type: ignore[call-arg]
            )

    def test_routing_rule_rejects_invalid_strategy(self) -> None:
        with pytest.raises(ValidationError):
            RoutingRule(
                rule_id="r1",
                match_strategy="magic",  # type: ignore[arg-type]
                match_value="x",
                target_persona="core",
            )

    def test_routing_result_no_match(self) -> None:
        r = RoutingResult(matched=False)
        assert r.rule_id is None
        assert r.target_persona is None

    def test_routing_result_match(self) -> None:
        r = RoutingResult(
            matched=True,
            rule_id="r1",
            target_persona="docs",
            target_agent="writer",
        )
        assert r.target_agent == "writer"


# ── intent router ─────────────────────────────────────────────────────────

class TestIntentRouter:
    @staticmethod
    def _make_router() -> IntentRouter:
        router = IntentRouter()
        router.add_rule(
            RoutingRule(
                rule_id="infra-deploy",
                match_strategy="keyword",
                match_value="deploy",
                target_persona="infra",
                priority=10,
            )
        )
        router.add_rule(
            RoutingRule(
                rule_id="docs-readme",
                match_strategy="keyword",
                match_value="readme",
                target_persona="docs",
                priority=5,
            )
        )
        router.add_rule(
            RoutingRule(
                rule_id="core-refactor",
                match_strategy="pattern",
                match_value=r"refactor|restructure",
                target_persona="core",
                priority=8,
            )
        )
        return router

    def test_keyword_match(self) -> None:
        router = self._make_router()
        result = router.route("please deploy the service")
        assert result.matched is True
        assert result.rule_id == "infra-deploy"
        assert result.target_persona == "infra"

    def test_keyword_case_insensitive(self) -> None:
        router = self._make_router()
        result = router.route("Update the README file")
        assert result.matched is True
        assert result.rule_id == "docs-readme"

    def test_pattern_match(self) -> None:
        router = self._make_router()
        result = router.route("restructure the module layout")
        assert result.matched is True
        assert result.rule_id == "core-refactor"

    def test_no_match_returns_unmatched(self) -> None:
        router = self._make_router()
        result = router.route("buy groceries")
        assert result.matched is False
        assert result.rule_id is None

    def test_priority_ordering(self) -> None:
        """Higher priority wins even if lower-priority rule was added first."""
        router = IntentRouter()
        router.add_rule(
            RoutingRule(
                rule_id="low",
                match_strategy="keyword",
                match_value="fix",
                target_persona="docs",
                priority=1,
            )
        )
        router.add_rule(
            RoutingRule(
                rule_id="high",
                match_strategy="keyword",
                match_value="fix",
                target_persona="core",
                priority=100,
            )
        )
        result = router.route("fix this bug")
        assert result.rule_id == "high"
        assert result.target_persona == "core"

    def test_disabled_rule_skipped(self) -> None:
        router = IntentRouter()
        router.add_rule(
            RoutingRule(
                rule_id="off",
                match_strategy="keyword",
                match_value="deploy",
                target_persona="infra",
                enabled=False,
            )
        )
        result = router.route("deploy now")
        assert result.matched is False

    def test_add_duplicate_raises(self) -> None:
        router = IntentRouter()
        rule = RoutingRule(
            rule_id="dup",
            match_strategy="keyword",
            match_value="x",
            target_persona="core",
        )
        router.add_rule(rule)
        with pytest.raises(ValueError, match="Duplicate"):
            router.add_rule(rule)

    def test_remove_rule(self) -> None:
        router = self._make_router()
        assert router.remove_rule("docs-readme") is True
        assert router.remove_rule("nonexistent") is False
        assert len(router.list_rules()) == 2

    def test_list_rules_sorted(self) -> None:
        router = self._make_router()
        ids = [r.rule_id for r in router.list_rules()]
        assert ids == ["infra-deploy", "core-refactor", "docs-readme"]

    def test_target_agent_forwarded(self) -> None:
        router = IntentRouter()
        router.add_rule(
            RoutingRule(
                rule_id="specific",
                match_strategy="keyword",
                match_value="compile",
                target_persona="core",
                target_agent="compiler-agent",
            )
        )
        result = router.route("compile the project")
        assert result.target_agent == "compiler-agent"

    def test_empty_router_returns_no_match(self) -> None:
        router = IntentRouter()
        result = router.route("anything")
        assert result.matched is False
