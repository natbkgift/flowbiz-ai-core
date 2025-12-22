"""Agent execution API endpoint."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from packages.core.agents import AgentResult, AgentRuntime
from packages.core.logging import REQUEST_ID_CTX_VAR
from packages.core.schemas.base import BaseSchema

router = APIRouter(prefix="/v1")


class AgentRunRequest(BaseSchema):
    """Request schema for agent execution."""

    input_text: str
    user_id: str | None = None
    client_id: str | None = None
    channel: str = "api"
    metadata: dict[str, Any] = {}


_runtime = AgentRuntime()


@router.post("/agent/run", summary="Execute agent", response_model=AgentResult)
def run_agent(request: Request, body: AgentRunRequest) -> AgentResult:
    """Execute the default agent with the provided input."""

    request_id = REQUEST_ID_CTX_VAR.get()

    return _runtime.run(
        input_text=body.input_text,
        request_id=request_id,
        user_id=body.user_id,
        client_id=body.client_id,
        channel=body.channel,
        metadata=body.metadata,
    )
