"""Step-based execution pipeline runner.

Evaluates an ordered list of pipeline steps, calling registered
handlers in sequence and respecting stop conditions.
"""

from __future__ import annotations

from typing import Any, Callable

from packages.core.contracts.pipeline import (
    PipelineResult,
    PipelineSpec,
    StepResult,
)

StepHandler = Callable[[dict[str, Any]], Any]
"""Signature for step handlers: receives context dict, returns output."""


class PipelineRunner:
    """In-memory synchronous pipeline executor."""

    def __init__(self) -> None:
        self._handlers: dict[str, StepHandler] = {}

    def register_handler(self, name: str, handler: StepHandler) -> None:
        """Register a callable as a step handler."""
        self._handlers[name] = handler

    def run(
        self, spec: PipelineSpec, context: dict[str, Any] | None = None
    ) -> PipelineResult:
        """Execute *spec* and return aggregate results."""
        ctx = dict(context or {})
        results: list[StepResult] = []
        overall = "completed"

        for step in spec.steps:
            if not step.enabled:
                results.append(StepResult(step_name=step.step_name, status="skipped"))
                continue

            handler = self._handlers.get(step.handler)
            if handler is None:
                result = StepResult(
                    step_name=step.step_name,
                    status="failed",
                    error=f"No handler registered for '{step.handler}'",
                )
                results.append(result)
                overall = "failed"
                if step.stop_condition in ("on_error", "always"):
                    break
                continue

            try:
                output = handler(ctx)
                result = StepResult(
                    step_name=step.step_name, status="completed", output=output
                )
                results.append(result)
                if step.stop_condition in ("on_success", "always"):
                    break
            except Exception as exc:
                result = StepResult(
                    step_name=step.step_name,
                    status="failed",
                    error=str(exc),
                )
                results.append(result)
                overall = "failed"
                if step.stop_condition in ("on_error", "always"):
                    break

        return PipelineResult(
            pipeline_name=spec.pipeline_name,
            status=overall,
            step_results=results,
        )
