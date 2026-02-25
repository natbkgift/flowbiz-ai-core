"""Tests for performance & scale contracts — PR-091 to PR-100."""

from __future__ import annotations

import time

from packages.core.contracts.performance import (
    AsyncTask,
    AsyncTaskResult,
    AutoscaleDecision,
    AutoscalePolicy,
    CacheConfig,
    ClusterState,
    CostOptimizationSuggestion,
    InMemoryCache,
    InMemoryTaskQueue,
    IndexRecommendation,
    LoadTestResult,
    LoadTestScenario,
    QueryPlan,
    QueueMessage,
    QueueStats,
    ReadReplicaConfig,
    ReadReplicaState,
    ResourceUsage,
    ScaleReadinessCheck,
    ScaleReadinessReport,
    ScalingNode,
)


# ---------------------------------------------------------------------------
# PR-091 — Async optimization
# ---------------------------------------------------------------------------


class TestAsyncTask:
    def test_create_task(self) -> None:
        t = AsyncTask(task_id="t-1", name="process_data")
        assert t.task_id == "t-1"
        assert t.status == "pending"
        assert t.error == ""

    def test_task_result(self) -> None:
        r = AsyncTaskResult(task_id="t-1", status="completed", progress_pct=100.0)
        assert r.progress_pct == 100.0
        assert r.result == {}


class TestInMemoryTaskQueue:
    def test_submit_and_get(self) -> None:
        q = InMemoryTaskQueue()
        task = AsyncTask(task_id="t-1", name="job")
        q.submit(task)
        assert q.get("t-1") is not None
        assert q.get("missing") is None

    def test_pending_filter(self) -> None:
        q = InMemoryTaskQueue()
        q.submit(AsyncTask(task_id="t-1", name="a"))
        q.submit(AsyncTask(task_id="t-2", name="b", status="running"))
        assert len(q.pending()) == 1

    def test_clear(self) -> None:
        q = InMemoryTaskQueue()
        q.submit(AsyncTask(task_id="t-1", name="a"))
        q.clear()
        assert q.get("t-1") is None


# ---------------------------------------------------------------------------
# PR-092 — Caching layer
# ---------------------------------------------------------------------------


class TestCacheConfig:
    def test_defaults(self) -> None:
        c = CacheConfig(name="main")
        assert c.strategy == "lru"
        assert c.max_size == 1000
        assert c.ttl_seconds == 300
        assert c.enabled is True


class TestInMemoryCache:
    def test_set_and_get(self) -> None:
        cache = InMemoryCache(CacheConfig(name="test", ttl_seconds=60))
        cache.set("k1", "v1")
        assert cache.get("k1") == "v1"

    def test_miss_returns_none(self) -> None:
        cache = InMemoryCache()
        assert cache.get("nope") is None

    def test_ttl_expiry(self) -> None:
        cache = InMemoryCache(CacheConfig(name="ttl", ttl_seconds=0))
        cache.set("k1", "v1", ttl=0)
        # TTL of 0 means expires immediately
        time.sleep(0.01)
        assert cache.get("k1") is None

    def test_delete(self) -> None:
        cache = InMemoryCache()
        cache.set("k1", "v1")
        assert cache.delete("k1") is True
        assert cache.delete("k1") is False

    def test_stats_hit_rate(self) -> None:
        cache = InMemoryCache(CacheConfig(name="stats"))
        cache.set("k1", "v1")
        cache.get("k1")  # hit
        cache.get("k2")  # miss
        s = cache.stats()
        assert s.hits == 1
        assert s.misses == 1
        assert s.hit_rate == 0.5
        assert s.size == 1

    def test_max_size_eviction(self) -> None:
        cache = InMemoryCache(CacheConfig(name="small", max_size=2))
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        assert cache.stats().size == 2

    def test_clear(self) -> None:
        cache = InMemoryCache()
        cache.set("k", 1)
        cache.get("k")
        cache.clear()
        s = cache.stats()
        assert s.size == 0
        assert s.hits == 0


# ---------------------------------------------------------------------------
# PR-093 — Queue backend
# ---------------------------------------------------------------------------


class TestQueueContracts:
    def test_queue_message(self) -> None:
        m = QueueMessage(message_id="m-1", queue_name="tasks", priority="high")
        assert m.priority == "high"
        assert m.retry_count == 0
        assert m.max_retries == 3

    def test_queue_stats(self) -> None:
        s = QueueStats(queue_name="tasks", pending=5, processing=2)
        assert s.pending == 5
        assert s.completed == 0


# ---------------------------------------------------------------------------
# PR-094 — Worker autoscale
# ---------------------------------------------------------------------------


class TestAutoscale:
    def test_autoscale_policy(self) -> None:
        p = AutoscalePolicy(name="default")
        assert p.min_replicas == 1
        assert p.max_replicas == 10
        assert p.target_cpu_pct == 70

    def test_autoscale_decision(self) -> None:
        d = AutoscaleDecision(current_replicas=2, desired_replicas=5, reason="high CPU")
        assert d.desired_replicas == 5
        assert d.reason == "high CPU"


# ---------------------------------------------------------------------------
# PR-095 — DB optimization
# ---------------------------------------------------------------------------


class TestDBOptimization:
    def test_query_plan(self) -> None:
        qp = QueryPlan(
            query="SELECT * FROM agents",
            estimated_cost=12.5,
            suggestions=("add index on id",),
        )
        assert qp.estimated_cost == 12.5
        assert len(qp.suggestions) == 1

    def test_index_recommendation(self) -> None:
        ir = IndexRecommendation(
            table="agents",
            columns=("name", "created_at"),
            estimated_improvement_pct=40.0,
            reason="frequent ORDER BY",
        )
        assert ir.index_type == "btree"
        assert ir.estimated_improvement_pct == 40.0


# ---------------------------------------------------------------------------
# PR-096 — Read replica
# ---------------------------------------------------------------------------


class TestReadReplica:
    def test_config(self) -> None:
        c = ReadReplicaConfig(replica_id="r-1", host="db-replica-1.local")
        assert c.port == 5432
        assert c.weight == 1

    def test_state(self) -> None:
        s = ReadReplicaState(replica_id="r-1", status="ready", lag_seconds=0.2)
        assert s.status == "ready"
        assert s.lag_seconds == 0.2


# ---------------------------------------------------------------------------
# PR-097 — Horizontal scaling
# ---------------------------------------------------------------------------


class TestHorizontalScaling:
    def test_scaling_node(self) -> None:
        n = ScalingNode(node_id="n-1", host="10.0.0.1", status="healthy")
        assert n.status == "healthy"
        assert n.active_connections == 0

    def test_cluster_state(self) -> None:
        nodes = (
            ScalingNode(node_id="n-1", host="10.0.0.1", status="healthy"),
            ScalingNode(node_id="n-2", host="10.0.0.2", status="draining"),
        )
        cs = ClusterState(
            nodes=nodes,
            healthy_count=1,
            total_count=2,
            leader_node_id="n-1",
        )
        assert cs.healthy_count == 1
        assert cs.leader_node_id == "n-1"


# ---------------------------------------------------------------------------
# PR-098 — Load testing suite
# ---------------------------------------------------------------------------


class TestLoadTesting:
    def test_scenario(self) -> None:
        s = LoadTestScenario(
            name="health_check",
            target_url="https://flowbiz.cloud/api/healthz",
            concurrent_users=50,
            duration_seconds=120,
        )
        assert s.method == "GET"
        assert s.ramp_up_seconds == 10

    def test_result(self) -> None:
        r = LoadTestResult(
            scenario_name="health_check",
            total_requests=6000,
            successful_requests=5990,
            failed_requests=10,
            avg_response_time_ms=45.2,
            p95_response_time_ms=120.0,
            p99_response_time_ms=250.0,
            requests_per_second=50.0,
        )
        assert r.successful_requests == 5990
        assert r.requests_per_second == 50.0


# ---------------------------------------------------------------------------
# PR-099 — Cost optimization
# ---------------------------------------------------------------------------


class TestCostOptimization:
    def test_resource_usage(self) -> None:
        u = ResourceUsage(
            resource_type="compute",
            current_usage=2.0,
            allocated=4.0,
            unit="vCPU",
            utilization_pct=50.0,
        )
        assert u.utilization_pct == 50.0
        assert u.unit == "vCPU"

    def test_suggestion(self) -> None:
        s = CostOptimizationSuggestion(
            title="Right-size compute",
            description="Reduce from 4 to 2 vCPU",
            estimated_savings_monthly_cents=5000,
            effort="low",
            priority="high",
        )
        assert s.estimated_savings_monthly_cents == 5000


# ---------------------------------------------------------------------------
# PR-100 — Scale readiness review
# ---------------------------------------------------------------------------


class TestScaleReadiness:
    def test_check(self) -> None:
        c = ScaleReadinessCheck(
            name="DB connection pooling",
            category="database",
            status="ready",
            recommendations=("Use PgBouncer",),
        )
        assert c.status == "ready"
        assert len(c.recommendations) == 1

    def test_report(self) -> None:
        checks = (
            ScaleReadinessCheck(name="caching", status="ready"),
            ScaleReadinessCheck(name="CDN", status="needs_work"),
        )
        r = ScaleReadinessReport(
            report_id="sr-1",
            checks=checks,
            overall_status="needs_work",
            target_rps=1000,
            current_rps=200,
            assessor="bot",
        )
        assert r.overall_status == "needs_work"
        assert len(r.checks) == 2
        assert r.target_rps == 1000

    def test_immutability(self) -> None:
        import pytest

        r = ScaleReadinessReport(report_id="sr-1")
        with pytest.raises(Exception):
            r.report_id = "changed"  # type: ignore[misc]
