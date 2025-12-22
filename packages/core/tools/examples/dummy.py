"""Deterministic echo tool example for ToolBase implementations."""

from __future__ import annotations

from typing import ClassVar

from packages.core.tools import ToolBase, ToolContext, ToolError, ToolResult


class DummyTool(ToolBase):
    """A minimal echo tool used as a golden reference implementation.

    This tool demonstrates how to implement the ToolBase contract without
    side effects. It either echoes the provided parameters or returns a
    structured error when no parameters are supplied.
    """

    name: ClassVar[str] = "dummy.echo"
    description: ClassVar[str] = "Echo back provided params for testing and examples"
    version: ClassVar[str] = "v1"

    def run(self, context: ToolContext) -> ToolResult:
        """Echo provided params or return an explicit empty-params error."""

        if not context.params:
            return ToolResult(
                ok=False,
                data=None,
                error=ToolError(
                    code="EMPTY_PARAMS",
                    message="No params provided",
                    retryable=False,
                ),
                trace_id=context.trace_id,
                tool_name=self.name,
            )

        return ToolResult(
            ok=True,
            data=dict(context.params),
            error=None,
            trace_id=context.trace_id,
            tool_name=self.name,
        )
