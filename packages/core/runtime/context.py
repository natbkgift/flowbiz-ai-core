"""Runtime context for agent execution."""

from __future__ import annotations

import uuid
from typing import Any


class RuntimeContext:
    """Minimal execution context for agent runtime."""

    def __init__(
        self,
        agent: str,
        input: str,
        trace_id: str | None = None,
        mode: str = "dev",
        meta: dict[str, Any] | None = None,
    ):
        """Create a new RuntimeContext.

        Args:
            agent: Agent name to execute
            input: Input string for the agent
            trace_id: Optional trace ID (generated if not provided)
            mode: Execution mode (default: "dev")
            meta: Additional metadata
        """
        self.agent = agent
        self.input = input
        self.trace_id = trace_id or str(uuid.uuid4())
        self.mode = mode
        self.meta = {} if meta is None else meta
