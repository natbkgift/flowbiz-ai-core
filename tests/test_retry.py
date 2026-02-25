"""Tests for retry/timeout/abort rules."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.retry import RetryPolicy, RetryResult, run_with_retry


class TestRetryPolicyContract:
    def test_defaults(self) -> None:
        p = RetryPolicy()
        assert p.max_retries == 3
        assert p.timeout_seconds == 30.0
        assert p.backoff_seconds == 0.0

    def test_frozen(self) -> None:
        p = RetryPolicy()
        with pytest.raises(ValidationError):
            p.max_retries = 5  # type: ignore[misc]

    def test_retry_result_schema(self) -> None:
        r = RetryResult(success=True, attempts=1, result="ok")
        assert r.success is True
        assert r.attempts == 1


class TestRunWithRetry:
    def test_success_first_try(self) -> None:
        result = run_with_retry(lambda: 42)
        assert result.success is True
        assert result.attempts == 1
        assert result.result == 42

    def test_success_after_failures(self) -> None:
        counter = {"n": 0}

        def flaky() -> str:
            counter["n"] += 1
            if counter["n"] < 3:
                raise RuntimeError("not yet")
            return "ok"

        result = run_with_retry(flaky)
        assert result.success is True
        assert result.attempts == 3

    def test_all_retries_exhausted(self) -> None:
        def fail() -> None:
            raise RuntimeError("always fails")

        result = run_with_retry(fail, RetryPolicy(max_retries=2))
        assert result.success is False
        assert result.attempts == 2
        assert result.error == "always fails"

    def test_abort_on_specific_exception(self) -> None:
        def bad() -> None:
            raise ValueError("fatal")

        result = run_with_retry(
            bad, RetryPolicy(max_retries=5, abort_on=["ValueError"])
        )
        assert result.success is False
        assert result.attempts == 1
        assert "Aborted" in (result.error or "")

    def test_default_policy_used(self) -> None:
        result = run_with_retry(lambda: "ok")
        assert result.success is True

    def test_backoff_respected(self) -> None:
        import time

        counter = {"n": 0}

        def flaky() -> str:
            counter["n"] += 1
            if counter["n"] < 2:
                raise RuntimeError("fail")
            return "ok"

        start = time.monotonic()
        result = run_with_retry(flaky, RetryPolicy(max_retries=3, backoff_seconds=0.05))
        elapsed = time.monotonic() - start
        assert result.success is True
        assert elapsed >= 0.04  # at least one backoff
