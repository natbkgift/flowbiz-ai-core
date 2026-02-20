"""Test fixture: Invalid tool that violates policy rules.

This tool intentionally violates multiple policy rules to ensure
the checker correctly detects them.
"""

from __future__ import annotations

import random  # VIOLATION: forbidden import
from typing import Any

from packages.core.tools.base import ToolBase
from packages.core.tools.context import ToolContext


class BadTool(ToolBase):
    """An invalid tool that violates multiple policy rules.

    This tool intentionally:
    - Imports random (forbidden)
    - Returns dict from run() (should return ToolResult)
    - Uses forbidden function calls
    """

    @property
    def name(self) -> str:
        """Return the unique name of this tool."""
        return "test.bad_tool"

    @property
    def description(self) -> str:
        """Return a description of what this tool does."""
        return "An invalid test tool for policy enforcement testing"

    # VIOLATION: missing version property (warning)

    def run(
        self, context: ToolContext
    ) -> dict[str, Any]:  # VIOLATION: wrong return type
        """Execute the tool with the given context.

        Args:
            context: Execution context containing input parameters and metadata

        Returns:
            Dict with output data (VIOLATION: should return ToolResult)
        """
        # VIOLATION: using random
        random_value = random.randint(1, 100)

        # VIOLATION: returning dict instead of ToolResult
        return {
            "ok": True,
            "data": {"random": random_value},
            "trace_id": context.trace_id,
        }
