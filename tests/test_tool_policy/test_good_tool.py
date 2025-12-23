"""Test fixture: Valid tool that passes all policy checks.

This tool demonstrates correct implementation that should pass
all enforced rules in the tool policy checker.
"""

from __future__ import annotations

from packages.core.tools.base import ToolBase
from packages.core.tools.context import ToolContext
from packages.core.tools.result import ToolError, ToolResult


class GoodTool(ToolBase):
    """A valid tool implementation that passes all policy checks.

    This tool:
    - Inherits from ToolBase
    - Defines all required attributes
    - Returns ToolResult from run()
    - Uses no forbidden imports
    - Has no side effects or randomness
    """

    @property
    def name(self) -> str:
        """Return the unique name of this tool."""
        return "test.good_tool"

    @property
    def description(self) -> str:
        """Return a description of what this tool does."""
        return "A valid test tool for policy enforcement testing"

    @property
    def version(self) -> str:
        """Return the version of this tool."""
        return "v1"

    def run(self, context: ToolContext) -> ToolResult:
        """Execute the tool with the given context.

        Args:
            context: Execution context containing input parameters and metadata

        Returns:
            Structured result containing output data or error information
        """
        # Validate params
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

        # Success path
        return ToolResult(
            ok=True,
            data={"processed": context.params},
            error=None,
            trace_id=context.trace_id,
            tool_name=self.name,
        )
