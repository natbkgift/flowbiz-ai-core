"""Agent execution context schema."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from packages.core.schemas.base import BaseSchema


class AgentContext(BaseSchema):
    """Normalized context for agent execution."""

    request_id: str | None = None
    user_id: str | None = None
    client_id: str | None = None
    channel: str = "api"
    input_text: str
    metadata: dict[str, Any] = {}
    created_at: datetime

    @classmethod
    def create(
        cls,
        input_text: str,
        request_id: str | None = None,
        user_id: str | None = None,
        client_id: str | None = None,
        channel: str = "api",
        metadata: dict[str, Any] | None = None,
    ) -> AgentContext:
        """Create a new AgentContext with current UTC timestamp."""

        return cls(
            request_id=request_id,
            user_id=user_id,
            client_id=client_id,
            channel=channel,
            input_text=input_text,
            metadata=metadata or {},
            created_at=datetime.now(timezone.utc),
        )
