"""Tests for execution pipeline contracts and runner."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.contracts.pipeline import (
    PipelineResult,
    PipelineSpec,
    PipelineStep,
    StepResult,
)
from packages.core.pipeline_runner import PipelineRunner


# ── contract tests ────────────────────────────────────────────────────────


class TestPipelineContracts:
    def test_step_frozen(self) -> None:
        s = PipelineStep(step_name="a", handler="h")
        with pytest.raises(ValidationError):
            s.step_name = "b"  # type: ignore[misc]

    def test_step_defaults(self) -> None:
        s = PipelineStep(step_name="a", handler="h")
        assert s.stop_condition == "on_error"
        assert s.enabled is True

    def test_step_result_frozen(self) -> None:
        r = StepResult(step_name="a", status="completed")
        with pytest.raises(ValidationError):
            r.status = "failed"  # type: ignore[misc]

    def test_pipeline_spec_frozen(self) -> None:
        p = PipelineSpec(pipeline_name="p")
        with pytest.raises(ValidationError):
            p.pipeline_name = "q"  # type: ignore[misc]

    def test_pipeline_result_frozen(self) -> None:
        r = PipelineResult(pipeline_name="p", status="completed")
        with pytest.raises(ValidationError):
            r.status = "failed"  # type: ignore[misc]

    def test_invalid_stop_condition(self) -> None:
        with pytest.raises(ValidationError):
            PipelineStep(step_name="a", handler="h", stop_condition="invalid")  # type: ignore[arg-type]


# ── runner tests ──────────────────────────────────────────────────────────


class TestPipelineRunner:
    def test_empty_pipeline(self) -> None:
        runner = PipelineRunner()
        spec = PipelineSpec(pipeline_name="empty")
        result = runner.run(spec)
        assert result.status == "completed"
        assert result.step_results == []

    def test_single_step_success(self) -> None:
        runner = PipelineRunner()
        runner.register_handler("echo", lambda ctx: "hello")
        spec = PipelineSpec(
            pipeline_name="one",
            steps=[PipelineStep(step_name="s1", handler="echo")],
        )
        result = runner.run(spec)
        assert result.status == "completed"
        assert len(result.step_results) == 1
        assert result.step_results[0].output == "hello"

    def test_multi_step_success(self) -> None:
        runner = PipelineRunner()
        runner.register_handler("a", lambda ctx: 1)
        runner.register_handler("b", lambda ctx: 2)
        spec = PipelineSpec(
            pipeline_name="multi",
            steps=[
                PipelineStep(step_name="s1", handler="a"),
                PipelineStep(step_name="s2", handler="b"),
            ],
        )
        result = runner.run(spec)
        assert result.status == "completed"
        assert len(result.step_results) == 2

    def test_step_failure_stops_on_error(self) -> None:
        runner = PipelineRunner()

        def fail(ctx: dict) -> None:
            raise RuntimeError("boom")

        runner.register_handler("fail", fail)
        runner.register_handler("ok", lambda ctx: "ok")
        spec = PipelineSpec(
            pipeline_name="halt",
            steps=[
                PipelineStep(step_name="s1", handler="fail", stop_condition="on_error"),
                PipelineStep(step_name="s2", handler="ok"),
            ],
        )
        result = runner.run(spec)
        assert result.status == "failed"
        assert len(result.step_results) == 1
        assert result.step_results[0].error == "boom"

    def test_step_failure_continues_on_never(self) -> None:
        runner = PipelineRunner()

        def fail(ctx: dict) -> None:
            raise RuntimeError("boom")

        runner.register_handler("fail", fail)
        runner.register_handler("ok", lambda ctx: "ok")
        spec = PipelineSpec(
            pipeline_name="continue",
            steps=[
                PipelineStep(step_name="s1", handler="fail", stop_condition="never"),
                PipelineStep(step_name="s2", handler="ok"),
            ],
        )
        result = runner.run(spec)
        assert result.status == "failed"
        assert len(result.step_results) == 2
        assert result.step_results[1].status == "completed"

    def test_disabled_step_skipped(self) -> None:
        runner = PipelineRunner()
        runner.register_handler("h", lambda ctx: 1)
        spec = PipelineSpec(
            pipeline_name="skip",
            steps=[
                PipelineStep(step_name="s1", handler="h", enabled=False),
                PipelineStep(step_name="s2", handler="h"),
            ],
        )
        result = runner.run(spec)
        assert result.step_results[0].status == "skipped"
        assert result.step_results[1].status == "completed"

    def test_missing_handler_fails(self) -> None:
        runner = PipelineRunner()
        spec = PipelineSpec(
            pipeline_name="missing",
            steps=[PipelineStep(step_name="s1", handler="nope")],
        )
        result = runner.run(spec)
        assert result.status == "failed"
        assert "No handler" in (result.step_results[0].error or "")

    def test_stop_on_success(self) -> None:
        runner = PipelineRunner()
        runner.register_handler("h", lambda ctx: "done")
        spec = PipelineSpec(
            pipeline_name="early",
            steps=[
                PipelineStep(step_name="s1", handler="h", stop_condition="on_success"),
                PipelineStep(step_name="s2", handler="h"),
            ],
        )
        result = runner.run(spec)
        assert result.status == "completed"
        assert len(result.step_results) == 1

    def test_context_passed_to_handler(self) -> None:
        captured: dict = {}

        def capture(ctx: dict) -> str:
            captured.update(ctx)
            return "ok"

        runner = PipelineRunner()
        runner.register_handler("cap", capture)
        spec = PipelineSpec(
            pipeline_name="ctx",
            steps=[PipelineStep(step_name="s1", handler="cap")],
        )
        runner.run(spec, context={"key": "value"})
        assert captured == {"key": "value"}
