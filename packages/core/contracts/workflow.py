"""Workflow contracts — PR-044.1 through PR-044.10.

Covers: workflow schema v2, step conditions, parallel steps, HITL,
pause/resume, state persistence contract, audit trail, replay,
import/export, and visual workflow JSON spec.

These are schema-only contracts; actual orchestration lives in the
pipeline runner or future workflow engine.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# ── PR-044.1: Workflow schema v2 ─────────────────────────────

WorkflowStatus = Literal[
    "pending", "running", "paused", "completed", "failed", "cancelled"
]

StepType = Literal["action", "condition", "parallel", "human", "sub_workflow"]


class WorkflowStepDef(BaseModel):
    """A single step definition inside a workflow spec."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_id: str = Field(..., description="Unique step identifier within workflow")
    step_type: StepType = Field("action", description="Step classification")
    name: str = Field(..., description="Human-readable step name")
    description: str = Field("", description="Step purpose")
    handler: str = Field(..., description="Handler identifier to execute")
    inputs: dict[str, Any] = Field(default_factory=dict, description="Static inputs")
    depends_on: list[str] = Field(
        default_factory=list, description="Step IDs this step depends on"
    )
    condition: str | None = Field(
        None, description="SpEL/jinja condition expression (PR-044.2)"
    )
    timeout_seconds: float = Field(0.0, description="Per-step timeout (0=unlimited)")
    retry_max: int = Field(0, description="Max retries on failure")
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowSpec(BaseModel):
    """Complete workflow specification (v2)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    workflow_id: str = Field(..., description="Unique workflow identifier")
    name: str = Field(..., description="Workflow name")
    version: str = Field("1.0.0", description="Semantic version")
    description: str = Field("", description="Workflow purpose")
    steps: list[WorkflowStepDef] = Field(
        default_factory=list, description="Ordered step definitions"
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


# ── PR-044.2: Step condition engine ──────────────────────────


class StepCondition(BaseModel):
    """Condition evaluated before a step executes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    expression: str = Field(
        ..., description="Condition expression (simple Python-like)"
    )
    description: str = Field("", description="Human-readable explanation")


def evaluate_condition(expression: str, context: dict[str, Any]) -> bool:
    """Evaluate a simple condition expression against context vars.

    Supports: ``key == value``, ``key != value``, ``key in list``,
    ``true``, ``false``.  This is intentionally minimal for safety.
    """
    expr = expression.strip().lower()
    if expr in ("true", "1", "yes"):
        return True
    if expr in ("false", "0", "no"):
        return False
    # Simple equality: "status == ok"
    for op, negate in [("!=", True), ("==", False)]:
        if op in expression:
            key, val = (
                s.strip().strip('"').strip("'") for s in expression.split(op, 1)
            )
            actual = str(context.get(key, ""))
            return (actual != val) if negate else (actual == val)
    return False


# ── PR-044.3: Parallel steps ────────────────────────────────


class ParallelGroup(BaseModel):
    """A group of steps that can execute in parallel."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    group_id: str = Field(..., description="Parallel group identifier")
    step_ids: list[str] = Field(default_factory=list, description="Steps in this group")
    join_strategy: Literal["all", "any"] = Field(
        "all", description="How to join parallel results"
    )


# ── PR-044.4: Human-in-the-loop ──────────────────────────────

HITLStatus = Literal["pending", "approved", "rejected", "timeout"]


class HITLRequest(BaseModel):
    """A request for human approval/input."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    request_id: str = Field(..., description="Unique HITL request identifier")
    workflow_id: str = Field(..., description="Parent workflow")
    step_id: str = Field(..., description="Step awaiting human input")
    prompt: str = Field(..., description="What the human needs to decide")
    options: list[str] = Field(default_factory=list, description="Available choices")
    status: HITLStatus = Field("pending")
    response: str | None = Field(None, description="Human's response")
    metadata: dict[str, Any] = Field(default_factory=dict)


# ── PR-044.5: Workflow pause / resume ────────────────────────


class WorkflowPauseEvent(BaseModel):
    """Event emitted when a workflow is paused."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    workflow_id: str
    reason: str = Field("manual", description="Pause reason")
    paused_at_step: str | None = Field(None, description="Step where pause occurred")


class WorkflowResumeEvent(BaseModel):
    """Event emitted when a workflow resumes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    workflow_id: str
    resumed_from_step: str | None = None


# ── PR-044.6: Workflow state persistence contract ────────────


class WorkflowState(BaseModel):
    """Serialisable snapshot of workflow execution state."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    workflow_id: str
    status: WorkflowStatus = Field("pending")
    current_step: str | None = Field(None, description="Currently executing step")
    completed_steps: list[str] = Field(default_factory=list)
    step_results: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(
        default_factory=dict, description="Shared workflow context"
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowStatePersistenceProtocol:
    """Abstract interface for workflow state persistence.

    Implementations should provide save/load/delete for WorkflowState.
    This is a stub — actual backends (Redis, DB) live outside core.
    """

    def save(self, state: WorkflowState) -> None:
        raise NotImplementedError

    def load(self, workflow_id: str) -> WorkflowState | None:
        raise NotImplementedError

    def delete(self, workflow_id: str) -> bool:
        raise NotImplementedError


class InMemoryWorkflowStateStore(WorkflowStatePersistenceProtocol):
    """In-memory stub for workflow state persistence."""

    def __init__(self) -> None:
        self._store: dict[str, WorkflowState] = {}

    def save(self, state: WorkflowState) -> None:
        self._store[state.workflow_id] = state

    def load(self, workflow_id: str) -> WorkflowState | None:
        return self._store.get(workflow_id)

    def delete(self, workflow_id: str) -> bool:
        return self._store.pop(workflow_id, None) is not None


# ── PR-044.7: Workflow audit trail ───────────────────────────

AuditAction = Literal[
    "workflow_started",
    "step_started",
    "step_completed",
    "step_failed",
    "workflow_paused",
    "workflow_resumed",
    "workflow_completed",
    "workflow_failed",
    "hitl_requested",
    "hitl_responded",
]


class WorkflowAuditEntry(BaseModel):
    """A single audit log entry for workflow execution."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    workflow_id: str
    action: AuditAction
    step_id: str | None = None
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    details: dict[str, Any] = Field(default_factory=dict)


# ── PR-044.8: Workflow replay ────────────────────────────────


class WorkflowReplayRequest(BaseModel):
    """Request to replay a workflow from audit trail."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    workflow_id: str
    from_step: str | None = Field(
        None, description="Step to replay from (None=beginning)"
    )
    dry_run: bool = Field(False, description="If True, simulate without side-effects")


# ── PR-044.9: Workflow import/export ─────────────────────────


class WorkflowExport(BaseModel):
    """Portable workflow definition for import/export."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    spec: WorkflowSpec
    version: str = Field("1.0.0", description="Export format version")
    exported_at: str = Field(..., description="ISO 8601 timestamp")
    checksum: str | None = Field(None, description="SHA256 of spec JSON")


# ── PR-044.10: Visual workflow JSON spec ─────────────────────


class WorkflowNodePosition(BaseModel):
    """XY position of a workflow node in visual editor."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_id: str
    x: float = Field(0.0)
    y: float = Field(0.0)


class WorkflowVisualSpec(BaseModel):
    """Visual layout metadata for workflow editor rendering."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    workflow_id: str
    positions: list[WorkflowNodePosition] = Field(default_factory=list)
    zoom: float = Field(1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
