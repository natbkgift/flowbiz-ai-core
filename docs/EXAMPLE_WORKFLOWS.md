# Example Workflows (PR-105)

## Purpose

Provide validated workflow example JSON stubs for developer reference using the existing workflow contracts from PR-044.1–044.10.

## Included Examples

- `docs/contracts/stubs/workflows/ticket-triage.workflow.json`
- `docs/contracts/stubs/workflows/approval-flow.workflow.json`
- `docs/contracts/stubs/workflows/ticket-triage.visual.json`

## Validation

`tests/test_workflow_examples.py` validates these stubs against:
- `WorkflowSpec`
- `WorkflowVisualSpec`

## Scope Notes

- No workflow executor/orchestrator changes
- No visual editor UI implementation
- Examples are contract-level reference assets only
