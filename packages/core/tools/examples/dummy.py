"""Deterministic echo tool example for ToolBase implementations."""

from __future__ import annotations

from packages.core.tools import ToolBase, ToolContext, ToolError, ToolResult


class DummyTool(ToolBase):
    """A minimal echo tool used as a golden reference implementation.

    This tool demonstrates how to implement the ToolBase contract without
    side effects. It either echoes the provided parameters or returns a
    structured error when no parameters are supplied.
    """

    _NAME = "dummy.echo"
    _DESCRIPTION = "Echo back provided params for testing and examples"
    _VERSION = "v1"

    @property
    def name(self) -> str:  # type: ignore[override]
        return self._NAME

    @property
    def description(self) -> str:  # type: ignore[override]
        return self._DESCRIPTION

    @property
    def version(self) -> str:  # type: ignore[override]
        return self._VERSION

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
