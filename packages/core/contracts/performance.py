"""Performance & scale contracts — PR-091 to PR-100.

Defines async optimization, caching, queue, worker autoscale,
DB optimization, read replica, horizontal scaling, load testing,
cost optimization, and scale readiness contracts.

Most infrastructure implementations live outside core; this module
provides **contracts and stubs**.

PR-091: Async optimization
PR-092: Caching layer
PR-093: Queue backend
PR-094: Worker autoscale
PR-095: DB optimization
PR-096: Read replica
PR-097: Horizontal scaling
PR-098: Load testing suite
PR-099: Cost optimization
PR-100: Scale readiness review
"""

from __future__ import annotations

import time
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# PR-091 — Async optimization
# ---------------------------------------------------------------------------

TaskStatus = Literal["pending", "running", "completed", "failed", "cancelled"]


class AsyncTask(BaseModel):
    """Contract for an async background task."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    task_id: str
    name: str
    status: TaskStatus = "pending"
    created_at: float = Field(default_factory=time.time)
    started_at: float | None = None
    completed_at: float | None = None
    result: dict[str, Any] = Field(default_factory=dict)
    error: str = ""


class AsyncTaskResult(BaseModel):
    """Result of polling an async task."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    task_id: str
    status: TaskStatus
    progress_pct: float = 0.0
    result: dict[str, Any] = Field(default_factory=dict)


class InMemoryTaskQueue:
    """In-memory async task queue stub."""

    def __init__(self) -> None:
        self._tasks: dict[str, AsyncTask] = {}

    def submit(self, task: AsyncTask) -> None:
        self._tasks[task.task_id] = task

    def get(self, task_id: str) -> AsyncTask | None:
        return self._tasks.get(task_id)

    def pending(self) -> list[AsyncTask]:
        return [t for t in self._tasks.values() if t.status == "pending"]

    def clear(self) -> None:
        self._tasks.clear()


# ---------------------------------------------------------------------------
# PR-092 — Caching layer
# ---------------------------------------------------------------------------

CacheStrategy = Literal["lru", "ttl", "lfu"]


class CacheConfig(BaseModel):
    """Cache configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    strategy: CacheStrategy = "lru"
    max_size: int = 1000
    ttl_seconds: int = 300
    enabled: bool = True


class CacheStats(BaseModel):
    """Cache performance statistics."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    hit_rate: float = 0.0


class InMemoryCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, config: CacheConfig | None = None) -> None:
        self._config = config or CacheConfig(name="default")
        self._store: dict[str, tuple[Any, float]] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            self._misses += 1
            return None
        value, expires_at = entry
        if time.time() > expires_at:
            del self._store[key]
            self._misses += 1
            return None
        self._hits += 1
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        ttl_val = ttl if ttl is not None else self._config.ttl_seconds
        self._store[key] = (value, time.time() + ttl_val)
        # Evict if over max size
        while len(self._store) > self._config.max_size:
            oldest = next(iter(self._store))
            del self._store[oldest]

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def stats(self) -> CacheStats:
        total = self._hits + self._misses
        return CacheStats(
            name=self._config.name,
            hits=self._hits,
            misses=self._misses,
            size=len(self._store),
            hit_rate=round(self._hits / total, 4) if total > 0 else 0.0,
        )

    def clear(self) -> None:
        self._store.clear()
        self._hits = 0
        self._misses = 0


# ---------------------------------------------------------------------------
# PR-093 — Queue backend
# ---------------------------------------------------------------------------

QueuePriority = Literal["low", "normal", "high", "critical"]


class QueueMessage(BaseModel):
    """Message in a task queue."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    message_id: str
    queue_name: str
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: QueuePriority = "normal"
    created_at: float = Field(default_factory=time.time)
    retry_count: int = 0
    max_retries: int = 3


class QueueStats(BaseModel):
    """Queue backend statistics."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    queue_name: str
    pending: int = 0
    processing: int = 0
    completed: int = 0
    failed: int = 0


# ---------------------------------------------------------------------------
# PR-094 — Worker autoscale
# ---------------------------------------------------------------------------


class AutoscalePolicy(BaseModel):
    """Autoscaling policy for workers."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    min_replicas: int = 1
    max_replicas: int = 10
    target_cpu_pct: int = 70
    target_queue_depth: int = 100
    scale_up_cooldown_seconds: int = 60
    scale_down_cooldown_seconds: int = 300


class AutoscaleDecision(BaseModel):
    """Result of an autoscale evaluation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    current_replicas: int
    desired_replicas: int
    reason: str = ""
    timestamp: float = Field(default_factory=time.time)


# ---------------------------------------------------------------------------
# PR-095 — DB optimization
# ---------------------------------------------------------------------------


class QueryPlan(BaseModel):
    """Captured query execution plan."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    query: str
    plan: str = ""
    estimated_cost: float = 0.0
    actual_duration_ms: float = 0.0
    suggestions: tuple[str, ...] = ()


class IndexRecommendation(BaseModel):
    """DB index recommendation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    table: str
    columns: tuple[str, ...]
    index_type: str = "btree"
    estimated_improvement_pct: float = 0.0
    reason: str = ""


# ---------------------------------------------------------------------------
# PR-096 — Read replica
# ---------------------------------------------------------------------------

ReplicaStatus = Literal["syncing", "ready", "lagging", "error"]


class ReadReplicaConfig(BaseModel):
    """Read replica configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    replica_id: str
    host: str
    port: int = 5432
    max_lag_seconds: int = 5
    weight: int = 1  # for load balancing


class ReadReplicaState(BaseModel):
    """Runtime state of a read replica."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    replica_id: str
    status: ReplicaStatus = "syncing"
    lag_seconds: float = 0.0
    connections_active: int = 0
    last_checked: float = Field(default_factory=time.time)


# ---------------------------------------------------------------------------
# PR-097 — Horizontal scaling
# ---------------------------------------------------------------------------

NodeStatus = Literal["healthy", "draining", "unhealthy", "starting"]


class ScalingNode(BaseModel):
    """Node in a horizontally-scaled cluster."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    node_id: str
    host: str
    status: NodeStatus = "starting"
    cpu_pct: float = 0.0
    memory_pct: float = 0.0
    active_connections: int = 0
    joined_at: float = Field(default_factory=time.time)


class ClusterState(BaseModel):
    """State of the horizontally-scaled cluster."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    nodes: tuple[ScalingNode, ...] = ()
    healthy_count: int = 0
    total_count: int = 0
    leader_node_id: str = ""


# ---------------------------------------------------------------------------
# PR-098 — Load testing suite
# ---------------------------------------------------------------------------


class LoadTestScenario(BaseModel):
    """Definition of a load test scenario."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    target_url: str
    method: str = "GET"
    concurrent_users: int = 10
    duration_seconds: int = 60
    ramp_up_seconds: int = 10
    headers: dict[str, str] = Field(default_factory=dict)
    body: dict[str, Any] = Field(default_factory=dict)


class LoadTestResult(BaseModel):
    """Result of a load test execution."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    scenario_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    p50_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    requests_per_second: float = 0.0
    duration_seconds: float = 0.0


# ---------------------------------------------------------------------------
# PR-099 — Cost optimization
# ---------------------------------------------------------------------------


class ResourceUsage(BaseModel):
    """Resource usage measurement for cost optimization."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    resource_type: str  # e.g. "compute", "storage", "network"
    current_usage: float
    allocated: float
    unit: str = ""
    cost_per_unit_cents: float = 0.0
    utilization_pct: float = 0.0


class CostOptimizationSuggestion(BaseModel):
    """Suggestion for reducing infrastructure costs."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    title: str
    description: str = ""
    estimated_savings_monthly_cents: int = 0
    effort: str = "low"  # low/medium/high
    priority: str = "medium"


# ---------------------------------------------------------------------------
# PR-100 — Scale readiness review
# ---------------------------------------------------------------------------

ReadinessStatus = Literal["ready", "needs_work", "not_assessed"]


class ScaleReadinessCheck(BaseModel):
    """Single check in a scale readiness review."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    category: str = ""  # e.g. "database", "api", "caching"
    status: ReadinessStatus = "not_assessed"
    notes: str = ""
    recommendations: tuple[str, ...] = ()


class ScaleReadinessReport(BaseModel):
    """Complete scale readiness assessment."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    report_id: str
    checks: tuple[ScaleReadinessCheck, ...] = ()
    overall_status: ReadinessStatus = "not_assessed"
    target_rps: int = 0  # target requests per second
    current_rps: int = 0
    assessed_at: float = Field(default_factory=time.time)
    assessor: str = ""
