"""Tests for workflow contracts — PR-044.1 through PR-044.10."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.contracts.workflow import (
    HITLRequest,
    InMemoryWorkflowStateStore,
    ParallelGroup,
    StepCondition,
    WorkflowAuditEntry,
    WorkflowExport,
    WorkflowNodePosition,
    WorkflowPauseEvent,
    WorkflowReplayRequest,
    WorkflowResumeEvent,
    WorkflowSpec,
    WorkflowState,
    WorkflowStepDef,
    WorkflowVisualSpec,
    evaluate_condition,
)


# ── Workflow schema v2 (PR-044.1) ────────────────────────────


class TestWorkflowSpec:
    def test_minimal_spec(self) -> None:
        s = WorkflowSpec(workflow_id="wf-1", name="My Workflow")
        assert s.workflow_id == "wf-1"
        assert s.steps == []

    def test_spec_with_steps(self) -> None:
        step = WorkflowStepDef(step_id="s1", name="Step 1", handler="echo")
        s = WorkflowSpec(workflow_id="wf-1", name="WF", steps=[step])
        assert len(s.steps) == 1

    def test_frozen(self) -> None:
        s = WorkflowSpec(workflow_id="wf-1", name="WF")
        with pytest.raises(ValidationError):
            s.name = "changed"  # type: ignore[misc]

    def test_step_def_defaults(self) -> None:
        d = WorkflowStepDef(step_id="s1", name="S1", handler="h")
        assert d.step_type == "action"
        assert d.depends_on == []
        assert d.condition is None


# ── Step condition engine (PR-044.2) ─────────────────────────


class TestStepCondition:
    def test_true_expression(self) -> None:
        assert evaluate_condition("true", {}) is True

    def test_false_expression(self) -> None:
        assert evaluate_condition("false", {}) is False

    def test_equality(self) -> None:
        assert evaluate_condition("status == ok", {"status": "ok"}) is True

    def test_inequality(self) -> None:
        assert evaluate_condition("status != ok", {"status": "fail"}) is True

    def test_missing_key(self) -> None:
        assert evaluate_condition("x == y", {}) is False

    def test_condition_model(self) -> None:
        c = StepCondition(expression="status == ok")
        assert c.expression == "status == ok"


# ── Parallel steps (PR-044.3) ────────────────────────────────


class TestParallelGroup:
    def test_defaults(self) -> None:
        g = ParallelGroup(group_id="g1")
        assert g.join_strategy == "all"
        assert g.step_ids == []

    def test_any_strategy(self) -> None:
        g = ParallelGroup(group_id="g1", step_ids=["a", "b"], join_strategy="any")
        assert g.join_strategy == "any"


# ── HITL (PR-044.4) ─────────────────────────────────────────


class TestHITL:
    def test_pending_by_default(self) -> None:
        h = HITLRequest(
            request_id="h1", workflow_id="wf-1", step_id="s1", prompt="Approve?"
        )
        assert h.status == "pending"
        assert h.response is None


# ── Pause / Resume (PR-044.5) ───────────────────────────────


class TestPauseResume:
    def test_pause_event(self) -> None:
        e = WorkflowPauseEvent(workflow_id="wf-1")
        assert e.reason == "manual"

    def test_resume_event(self) -> None:
        e = WorkflowResumeEvent(workflow_id="wf-1", resumed_from_step="s2")
        assert e.resumed_from_step == "s2"


# ── State persistence (PR-044.6) ────────────────────────────


class TestWorkflowState:
    def test_defaults(self) -> None:
        s = WorkflowState(workflow_id="wf-1")
        assert s.status == "pending"
        assert s.completed_steps == []

    def test_in_memory_store(self) -> None:
        store = InMemoryWorkflowStateStore()
        state = WorkflowState(workflow_id="wf-1", status="running")
        store.save(state)
        loaded = store.load("wf-1")
        assert loaded is not None
        assert loaded.status == "running"

    def test_store_delete(self) -> None:
        store = InMemoryWorkflowStateStore()
        store.save(WorkflowState(workflow_id="wf-x"))
        assert store.delete("wf-x") is True
        assert store.delete("wf-x") is False


# ── Audit trail (PR-044.7) ──────────────────────────────────


class TestAuditEntry:
    def test_entry(self) -> None:
        e = WorkflowAuditEntry(
            workflow_id="wf-1",
            action="workflow_started",
            timestamp="2026-01-01T00:00:00Z",
        )
        assert e.action == "workflow_started"


# ── Replay (PR-044.8) ───────────────────────────────────────


class TestReplay:
    def test_replay_request(self) -> None:
        r = WorkflowReplayRequest(workflow_id="wf-1", dry_run=True)
        assert r.dry_run is True
        assert r.from_step is None


# ── Import/Export (PR-044.9) ─────────────────────────────────


class TestExport:
    def test_export(self) -> None:
        spec = WorkflowSpec(workflow_id="wf-1", name="WF")
        e = WorkflowExport(spec=spec, exported_at="2026-01-01T00:00:00Z")
        assert e.version == "1.0.0"


# ── Visual spec (PR-044.10) ─────────────────────────────────


class TestVisualSpec:
    def test_positions(self) -> None:
        v = WorkflowVisualSpec(
            workflow_id="wf-1",
            positions=[WorkflowNodePosition(step_id="s1", x=100, y=200)],
        )
        assert len(v.positions) == 1
        assert v.positions[0].x == 100
