"""Observability metrics contracts — PR-051, PR-052.

Defines metric types, metric snapshots, and a pluggable metrics
collector interface.  Ships with an InMemoryMetricsCollector stub;
production backends (Prometheus, Datadog, etc.) live outside core.
"""

from __future__ import annotations

import time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Metric types
# ---------------------------------------------------------------------------

MetricKind = Literal["counter", "gauge", "histogram"]


class MetricDefinition(BaseModel):
    """Declarative metric registration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    kind: MetricKind
    description: str = ""
    labels: tuple[str, ...] = ()


class MetricSample(BaseModel):
    """Single observation for a metric."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    value: float
    labels: dict[str, str] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class MetricsSnapshot(BaseModel):
    """Point-in-time dump of all collected metrics."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    samples: tuple[MetricSample, ...] = ()
    collected_at: float = Field(default_factory=time.time)


# ---------------------------------------------------------------------------
# Prometheus exposition stub — PR-052
# ---------------------------------------------------------------------------


class PrometheusExposition(BaseModel):
    """Stub payload returned by a /metrics endpoint.

    Real Prometheus exposition is text-based; this contract wraps the
    text body so upstream code can treat it as structured data.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    content_type: str = "text/plain; version=0.0.4; charset=utf-8"
    body: str = ""


# ---------------------------------------------------------------------------
# Collector interface (in-memory stub)
# ---------------------------------------------------------------------------


class InMemoryMetricsCollector:
    """Minimal in-memory metrics collector for testing.

    NOT thread-safe — use a real backend for production.
    """

    def __init__(self) -> None:
        self._definitions: dict[str, MetricDefinition] = {}
        self._samples: list[MetricSample] = []

    # -- registration -------------------------------------------------------
    def register(self, defn: MetricDefinition) -> None:
        self._definitions[defn.name] = defn

    def definitions(self) -> list[MetricDefinition]:
        return list(self._definitions.values())

    # -- recording -----------------------------------------------------------
    def record(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        self._samples.append(MetricSample(name=name, value=value, labels=labels or {}))

    # -- querying ------------------------------------------------------------
    def snapshot(self) -> MetricsSnapshot:
        return MetricsSnapshot(samples=tuple(self._samples))

    def samples_for(self, name: str) -> list[MetricSample]:
        return [s for s in self._samples if s.name == name]

    # -- exposition ----------------------------------------------------------
    def to_prometheus(self) -> PrometheusExposition:
        """Render metrics in Prometheus text exposition format (simplified)."""
        lines: list[str] = []
        for defn in self._definitions.values():
            lines.append(f"# HELP {defn.name} {defn.description}")
            lines.append(f"# TYPE {defn.name} {defn.kind}")
        for sample in self._samples:
            label_str = ""
            if sample.labels:
                pairs = ",".join(f'{k}="{v}"' for k, v in sorted(sample.labels.items()))
                label_str = f"{{{pairs}}}"
            lines.append(f"{sample.name}{label_str} {sample.value}")
        return PrometheusExposition(body="\n".join(lines) + "\n" if lines else "")

    def clear(self) -> None:
        self._definitions.clear()
        self._samples.clear()
