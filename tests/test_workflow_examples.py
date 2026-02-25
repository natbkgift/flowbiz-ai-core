"""Validation tests for workflow example stubs (PR-105)."""

from __future__ import annotations

import json
from pathlib import Path

from packages.core.contracts.workflow import WorkflowSpec, WorkflowVisualSpec


STUB_DIR = Path("docs/contracts/stubs/workflows")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TestWorkflowExampleStubs:
    def test_ticket_triage_workflow_valid(self) -> None:
        payload = _load_json(STUB_DIR / "ticket-triage.workflow.json")
        spec = WorkflowSpec.model_validate(payload)
        assert spec.workflow_id == "ticket-triage"
        assert [step.step_id for step in spec.steps] == ["ingest", "classify", "assign"]

    def test_approval_flow_workflow_valid(self) -> None:
        payload = _load_json(STUB_DIR / "approval-flow.workflow.json")
        spec = WorkflowSpec.model_validate(payload)
        assert spec.workflow_id == "approval-flow"
        assert any(step.step_type == "human" for step in spec.steps)

    def test_visual_stub_valid(self) -> None:
        payload = _load_json(STUB_DIR / "ticket-triage.visual.json")
        visual = WorkflowVisualSpec.model_validate(payload)
        assert visual.workflow_id == "ticket-triage"
        assert len(visual.positions) == 3
