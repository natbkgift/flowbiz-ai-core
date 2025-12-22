"""Agent runtime orchestration with structured logging."""

from __future__ import annotations

from typing import Any

from packages.core.logging import get_logger

from .base import AgentBase
from .context import AgentContext
from .default_agent import DefaultAgent
from .result import AgentResult


class AgentRuntime:
    """Orchestrates agent execution with lifecycle event logging."""

    def __init__(self, agent: AgentBase | None = None):
        self.agent = agent or DefaultAgent()
        self.logger = get_logger("flowbiz.agents.runtime")

    def run(
        self,
        input_text: str,
        request_id: str | None = None,
        user_id: str | None = None,
        client_id: str | None = None,
        channel: str | None = "api",
        metadata: dict[str, Any] | None = None,
    ) -> AgentResult:
        """Build context, run agent, and return result with structured logging."""

        self.logger.info(
            "runtime_start",
            extra={
                "request_id": request_id,
                "channel": channel,
            },
        )

        ctx = AgentContext.create(
            input_text=input_text,
            request_id=request_id,
            user_id=user_id,
            client_id=client_id,
            channel=channel,
            metadata=metadata,
        )

        self.logger.info(
            "agent_selected",
            extra={
                "request_id": request_id,
                "agent_name": self.agent.name,
            },
        )

        result = self.agent.run(ctx)

        self.logger.info(
            "agent_done",
            extra={
                "request_id": request_id,
                "agent_name": self.agent.name,
                "status": result.status,
            },
        )

        self.logger.info(
            "runtime_done",
            extra={
                "request_id": request_id,
                "status": result.status,
            },
        )

        return result
