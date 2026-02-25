"""Tests for metrics contracts — PR-051, PR-052."""

from __future__ import annotations

from packages.core.contracts.metrics import (
    InMemoryMetricsCollector,
    MetricDefinition,
    MetricSample,
    MetricsSnapshot,
    PrometheusExposition,
)


class TestMetricDefinition:
    def test_schema(self) -> None:
        d = MetricDefinition(
            name="req_total", kind="counter", description="Total requests"
        )
        assert d.name == "req_total"
        assert d.kind == "counter"
        assert d.labels == ()

    def test_frozen(self) -> None:
        d = MetricDefinition(name="x", kind="gauge")
        try:
            d.name = "y"  # type: ignore[misc]
            assert False, "Should raise"
        except Exception:
            pass

    def test_metric_kind_literal(self) -> None:
        for k in ("counter", "gauge", "histogram"):
            d = MetricDefinition(name="m", kind=k)  # type: ignore[arg-type]
            assert d.kind == k


class TestMetricSample:
    def test_schema(self) -> None:
        s = MetricSample(name="req_total", value=42.0)
        assert s.name == "req_total"
        assert s.value == 42.0
        assert s.labels == {}
        assert s.timestamp > 0

    def test_with_labels(self) -> None:
        s = MetricSample(name="req_total", value=1.0, labels={"method": "GET"})
        assert s.labels["method"] == "GET"


class TestMetricsSnapshot:
    def test_empty(self) -> None:
        snap = MetricsSnapshot()
        assert snap.samples == ()
        assert snap.collected_at > 0


class TestPrometheusExposition:
    def test_default(self) -> None:
        p = PrometheusExposition()
        assert "text/plain" in p.content_type
        assert p.body == ""


class TestInMemoryMetricsCollector:
    def test_register_and_definitions(self) -> None:
        c = InMemoryMetricsCollector()
        d = MetricDefinition(name="req_total", kind="counter", description="Total")
        c.register(d)
        assert len(c.definitions()) == 1
        assert c.definitions()[0].name == "req_total"

    def test_record_and_snapshot(self) -> None:
        c = InMemoryMetricsCollector()
        c.record("req_total", 1.0)
        c.record("req_total", 2.0)
        snap = c.snapshot()
        assert len(snap.samples) == 2

    def test_samples_for(self) -> None:
        c = InMemoryMetricsCollector()
        c.record("a", 1.0)
        c.record("b", 2.0)
        c.record("a", 3.0)
        assert len(c.samples_for("a")) == 2
        assert len(c.samples_for("b")) == 1

    def test_to_prometheus(self) -> None:
        c = InMemoryMetricsCollector()
        c.register(
            MetricDefinition(name="req_total", kind="counter", description="Total")
        )
        c.record("req_total", 5.0)
        p = c.to_prometheus()
        assert "# HELP req_total Total" in p.body
        assert "# TYPE req_total counter" in p.body
        assert "req_total 5.0" in p.body

    def test_prometheus_with_labels(self) -> None:
        c = InMemoryMetricsCollector()
        c.record("req_total", 1.0, labels={"method": "GET"})
        p = c.to_prometheus()
        assert 'method="GET"' in p.body

    def test_clear(self) -> None:
        c = InMemoryMetricsCollector()
        c.register(MetricDefinition(name="x", kind="gauge"))
        c.record("x", 1.0)
        c.clear()
        assert c.definitions() == []
        assert c.snapshot().samples == ()
