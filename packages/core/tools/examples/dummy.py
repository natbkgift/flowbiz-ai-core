"""DummyTool: Reference implementation for Tool interface.

This is a canonical example tool that demonstrates:
- Correct ToolBase implementation
- ToolContext and ToolResult usage
- Deterministic execution with zero side effects
- Explicit error handling

This tool is NOT used in production and exists solely as a template
for creating new tools.
"""

from __future__ import annotations

from typing import Any

from ..base import ToolBase
from ..context import ToolContext
from ..result import ToolError, ToolResult


class DummyTool(ToolBase):
    """Echo tool that demonstrates proper Tool interface implementation.

    This tool accepts arbitrary parameters and echoes them back unchanged.
    It serves as a reference for implementing new tools and testing the
    Tool Registry and Agent Runtime.

    Behavior:
    - Empty/falsy params → EMPTY_PARAMS error
    - Invalid params (not dict-like) → INVALID_PARAMS error
    - Valid params → success with echoed data

    Properties:
    - Deterministic: no randomness, no time-based output
    - Side-effect free: no external calls, no env reads, no mutations
    - Error-safe: no exceptions escape run()
    """

    @property
    def name(self) -> str:
        """Return the unique name of this tool."""
        return "dummy.echo"

    @property
    def description(self) -> str:
        """Return a description of what this tool does."""
        return "Echo back provided params for testing and examples"

    @property
    def version(self) -> str:
        """Return the version of this tool."""
        return "v1"

    def run(self, context: ToolContext) -> ToolResult:
        """Execute the dummy echo tool.

        Args:
            context: Execution context containing input parameters and metadata

        Returns:
            ToolResult with echoed params on success, or error information
        """
        # Validate params is dict-like
        if not isinstance(context.params, dict):
            return ToolResult(
                ok=False,
                data=None,
                error=ToolError(
                    code="INVALID_PARAMS",
                    message="Params must be a dictionary",
                    retryable=False,
                ),
                trace_id=context.trace_id,
                tool_name=self.name,
            )

        # Check for empty/falsy params
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

        # Success path: echo params back
        echo_data: dict[str, Any] = {
            "echoed": context.params,
        }

        return ToolResult(
            ok=True,
            data=echo_data,
            error=None,
            trace_id=context.trace_id,
            tool_name=self.name,
        )
