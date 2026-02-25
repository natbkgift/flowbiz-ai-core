"""Tests for alerting and uptime monitoring contracts — PR-058, PR-059."""

from __future__ import annotations

from packages.core.contracts.alerting import (
    AlertEvent,
    AlertRule,
    InMemoryAlertStore,
    InMemoryUptimeStore,
    UptimeCheck,
    UptimeResult,
)


class TestAlertRule:
    def test_schema(self) -> None:
        r = AlertRule(name="high_error_rate", severity="critical", threshold=0.05)
        assert r.name == "high_error_rate"
        assert r.severity == "critical"
        assert r.evaluation_interval_seconds == 60

    def test_frozen(self) -> None:
        r = AlertRule(name="x")
        try:
            r.name = "y"  # type: ignore[misc]
            assert False, "Should raise"
        except Exception:
            pass


class TestAlertEvent:
    def test_schema(self) -> None:
        ev = AlertEvent(
            rule_name="cpu_high", status="firing", severity="warning", value=85.0
        )
        assert ev.status == "firing"
        assert ev.value == 85.0


class TestInMemoryAlertStore:
    def test_add_rule_and_fire(self) -> None:
        store = InMemoryAlertStore()
        store.add_rule(AlertRule(name="cpu_high", severity="critical", threshold=80.0))
        ev = store.fire("cpu_high", value=92.0, message="CPU at 92%")
        assert ev.status == "firing"
        assert ev.severity == "critical"
        assert len(store.events()) == 1

    def test_resolve(self) -> None:
        store = InMemoryAlertStore()
        store.add_rule(AlertRule(name="cpu_high", severity="critical"))
        store.fire("cpu_high", value=90.0)
        ev = store.resolve("cpu_high")
        assert ev.status == "resolved"
        assert len(store.events()) == 2

    def test_firing_filter(self) -> None:
        store = InMemoryAlertStore()
        store.add_rule(AlertRule(name="a", severity="warning"))
        store.fire("a", value=1.0)
        store.resolve("a")
        assert len(store.firing()) == 1  # both events exist, 1 firing

    def test_clear(self) -> None:
        store = InMemoryAlertStore()
        store.add_rule(AlertRule(name="x"))
        store.fire("x", value=1.0)
        store.clear()
        assert store.rules() == []
        assert store.events() == []


class TestUptimeCheck:
    def test_schema(self) -> None:
        c = UptimeCheck(name="api", url="https://flowbiz.cloud/api/healthz")
        assert c.interval_seconds == 60
        assert c.expected_status == 200


class TestUptimeResult:
    def test_schema(self) -> None:
        r = UptimeResult(
            check_name="api", status="up", response_time_ms=45.0, status_code=200
        )
        assert r.status == "up"


class TestInMemoryUptimeStore:
    def test_register_and_record(self) -> None:
        store = InMemoryUptimeStore()
        store.register(UptimeCheck(name="api", url="https://example.com"))
        store.record(UptimeResult(check_name="api", status="up", status_code=200))
        assert len(store.checks()) == 1
        assert store.latest("api") is not None
        assert store.latest("api").status == "up"

    def test_snapshot_overall_up(self) -> None:
        store = InMemoryUptimeStore()
        store.record(UptimeResult(check_name="a", status="up", status_code=200))
        store.record(UptimeResult(check_name="b", status="up", status_code=200))
        snap = store.snapshot()
        assert snap.overall_status == "up"

    def test_snapshot_overall_down(self) -> None:
        store = InMemoryUptimeStore()
        store.record(UptimeResult(check_name="a", status="up", status_code=200))
        store.record(UptimeResult(check_name="b", status="down", error="timeout"))
        snap = store.snapshot()
        assert snap.overall_status == "down"

    def test_snapshot_degraded(self) -> None:
        store = InMemoryUptimeStore()
        store.record(UptimeResult(check_name="a", status="up", status_code=200))
        store.record(UptimeResult(check_name="b", status="degraded", status_code=200))
        snap = store.snapshot()
        assert snap.overall_status == "degraded"

    def test_clear(self) -> None:
        store = InMemoryUptimeStore()
        store.register(UptimeCheck(name="x", url="http://x"))
        store.record(UptimeResult(check_name="x", status="up"))
        store.clear()
        assert store.checks() == []
