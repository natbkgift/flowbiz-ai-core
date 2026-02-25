"""Retry, timeout, and abort rules.

Provides a contract for retry policies and a simple retry executor
that wraps a callable with configurable retry/timeout/abort logic.
"""

from __future__ import annotations

import time
from typing import Any, Callable, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class RetryPolicy(BaseModel):
    """Retry policy configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    max_retries: int = Field(3, description="Maximum number of retry attempts")
    timeout_seconds: float = Field(
        30.0, description="Per-attempt timeout in seconds (0 = no timeout)"
    )
    backoff_seconds: float = Field(0.0, description="Seconds to wait between retries")
    abort_on: list[str] = Field(
        default_factory=list,
        description="Exception class names that should abort immediately",
    )


class RetryResult(BaseModel):
    """Outcome of a retried operation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    success: bool = Field(..., description="Whether the operation succeeded")
    attempts: int = Field(..., description="Total attempts made")
    result: Any = Field(None, description="Return value if successful")
    error: str | None = Field(None, description="Last error if failed")


def run_with_retry(
    fn: Callable[[], T],
    policy: RetryPolicy | None = None,
) -> RetryResult:
    """Execute *fn* with retry logic governed by *policy*.

    Note: ``timeout_seconds`` is advisory — the caller should implement
    actual timeout mechanisms (e.g., threading) if needed.  This
    implementation respects backoff and abort rules.
    """
    p = policy or RetryPolicy()
    last_error: str | None = None

    for attempt in range(1, p.max_retries + 1):
        try:
            value = fn()
            return RetryResult(success=True, attempts=attempt, result=value)
        except Exception as exc:
            last_error = str(exc)
            exc_name = type(exc).__name__
            if exc_name in p.abort_on:
                return RetryResult(
                    success=False, attempts=attempt, error=f"Aborted: {last_error}"
                )
            if attempt < p.max_retries and p.backoff_seconds > 0:
                time.sleep(p.backoff_seconds)

    return RetryResult(
        success=False,
        attempts=p.max_retries,
        error=last_error,
    )
