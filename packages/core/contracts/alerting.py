"""Alert rules and uptime monitoring contracts — PR-058, PR-059.

Defines alert rule evaluation, uptime check contracts, and in-memory
stores.  Actual alerting backends (PagerDuty, Slack, OpsGenie) and
uptime probes live outside core.
"""

from __future__ import annotations

import time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# PR-058 — Alert rules
# ---------------------------------------------------------------------------

AlertSeverity = Literal["info", "warning", "critical"]
AlertStatus = Literal["firing", "resolved", "silenced"]


class AlertRule(BaseModel):
    """Declarative alert rule definition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    description: str = ""
    severity: AlertSeverity = "warning"
    condition: str = ""  # human-readable condition expression
    threshold: float = 0.0
    evaluation_interval_seconds: int = 60


class AlertEvent(BaseModel):
    """Fired when an alert rule triggers or resolves."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rule_name: str
    status: AlertStatus
    severity: AlertSeverity
    message: str = ""
    value: float = 0.0
    timestamp: float = Field(default_factory=time.time)
    labels: dict[str, str] = Field(default_factory=dict)


class InMemoryAlertStore:
    """Tracks alert rules and events in-memory."""

    def __init__(self) -> None:
        self._rules: dict[str, AlertRule] = {}
        self._events: list[AlertEvent] = []

    def add_rule(self, rule: AlertRule) -> None:
        self._rules[rule.name] = rule

    def rules(self) -> list[AlertRule]:
        return list(self._rules.values())

    def fire(self, rule_name: str, value: float, message: str = "") -> AlertEvent:
        rule = self._rules.get(rule_name)
        severity = rule.severity if rule else "warning"
        event = AlertEvent(
            rule_name=rule_name,
            status="firing",
            severity=severity,
            message=message,
            value=value,
        )
        self._events.append(event)
        return event

    def resolve(self, rule_name: str) -> AlertEvent:
        rule = self._rules.get(rule_name)
        severity = rule.severity if rule else "info"
        event = AlertEvent(
            rule_name=rule_name,
            status="resolved",
            severity=severity,
        )
        self._events.append(event)
        return event

    def events(self) -> list[AlertEvent]:
        return list(self._events)

    def firing(self) -> list[AlertEvent]:
        return [e for e in self._events if e.status == "firing"]

    def clear(self) -> None:
        self._rules.clear()
        self._events.clear()


# ---------------------------------------------------------------------------
# PR-059 — Uptime monitoring
# ---------------------------------------------------------------------------

UptimeStatus = Literal["up", "down", "degraded"]


class UptimeCheck(BaseModel):
    """Configuration for an uptime probe."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    url: str
    interval_seconds: int = 60
    timeout_seconds: int = 10
    expected_status: int = 200


class UptimeResult(BaseModel):
    """Result of a single uptime check execution."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    check_name: str
    status: UptimeStatus
    response_time_ms: float = 0.0
    status_code: int = 0
    timestamp: float = Field(default_factory=time.time)
    error: str = ""


class UptimeSnapshot(BaseModel):
    """Current uptime state across all checks."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    checks: tuple[UptimeResult, ...] = ()
    overall_status: UptimeStatus = "up"
    collected_at: float = Field(default_factory=time.time)


class InMemoryUptimeStore:
    """Tracks uptime check configurations and results."""

    def __init__(self) -> None:
        self._checks: dict[str, UptimeCheck] = {}
        self._results: list[UptimeResult] = []

    def register(self, check: UptimeCheck) -> None:
        self._checks[check.name] = check

    def checks(self) -> list[UptimeCheck]:
        return list(self._checks.values())

    def record(self, result: UptimeResult) -> None:
        self._results.append(result)

    def latest(self, check_name: str) -> UptimeResult | None:
        for r in reversed(self._results):
            if r.check_name == check_name:
                return r
        return None

    def snapshot(self) -> UptimeSnapshot:
        latest_map: dict[str, UptimeResult] = {}
        for r in self._results:
            latest_map[r.check_name] = r
        results = tuple(latest_map.values())
        statuses = [r.status for r in results]
        if "down" in statuses:
            overall = "down"
        elif "degraded" in statuses:
            overall = "degraded"
        else:
            overall = "up"
        return UptimeSnapshot(checks=results, overall_status=overall)

    def clear(self) -> None:
        self._checks.clear()
        self._results.clear()
