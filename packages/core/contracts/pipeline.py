"""Execution pipeline contract schemas.

Defines the step-based execution pipeline: a sequence of named steps,
each with an optional stop condition, that are evaluated in order.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

StepStatus = Literal["pending", "running", "completed", "failed", "skipped"]
"""Lifecycle state of a pipeline step."""

StopCondition = Literal["on_error", "on_success", "always", "never"]
"""When the pipeline should halt after this step."""


class PipelineStep(BaseModel):
    """A single step in the execution pipeline."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_name: str = Field(..., description="Unique name within the pipeline")
    handler: str = Field(
        ..., description="Identifier of the callable that executes this step"
    )
    stop_condition: StopCondition = Field(
        "on_error", description="When to halt the pipeline after this step"
    )
    enabled: bool = Field(True, description="Whether the step is active")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary step metadata"
    )


class StepResult(BaseModel):
    """Outcome produced by running a pipeline step."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    step_name: str = Field(..., description="Step that produced this result")
    status: StepStatus = Field(..., description="Final status of the step")
    output: Any = Field(None, description="Return value of the step handler")
    error: str | None = Field(None, description="Error message if failed")


class PipelineSpec(BaseModel):
    """Specification of a full execution pipeline."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    pipeline_name: str = Field(..., description="Unique pipeline identifier")
    steps: list[PipelineStep] = Field(default_factory=list, description="Ordered steps")


class PipelineResult(BaseModel):
    """Aggregate result after the pipeline finishes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    pipeline_name: str = Field(..., description="Pipeline that ran")
    status: StepStatus = Field(
        ..., description="Overall pipeline status (completed/failed)"
    )
    step_results: list[StepResult] = Field(
        default_factory=list, description="Results for each step"
    )
