"""Runtime result schema."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class RuntimeError(BaseModel):
    """Error details in runtime result."""

    code: Literal["VALIDATION_ERROR", "AGENT_NOT_FOUND", "RUNTIME_ERROR"]
    message: str
    details: dict[str, Any] = {}

    model_config = ConfigDict(extra="forbid", frozen=False)


class RuntimeResult(BaseModel):
    """Result schema for agent runtime execution."""

    status: Literal["ok", "error"]
    trace_id: str
    agent: str | None
    output: str | None
    errors: list[RuntimeError]

    model_config = ConfigDict(extra="forbid")

    def __init__(self, **data):
        """Initialize RuntimeResult with default empty errors list."""
        if "errors" not in data:
            data["errors"] = []
        super().__init__(**data)
