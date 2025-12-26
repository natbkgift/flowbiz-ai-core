"""Agent execution API endpoint - PR-022 Runtime."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from packages.core.agents import AgentResult, AgentRuntime as LegacyRuntime
from packages.core.logging import REQUEST_ID_CTX_VAR
from packages.core.runtime import AgentRuntime, RuntimeContext, RuntimeRequest, RuntimeResult
from packages.core.schemas.base import BaseSchema

router = APIRouter(prefix="/v1")


class AgentRunRequest(BaseSchema):
    """Request schema for agent execution."""

    input_text: str
    user_id: str | None = None
    client_id: str | None = None
    channel: str = "api"
    metadata: dict[str, Any] = {}


_legacy_runtime = LegacyRuntime()
_runtime = AgentRuntime()


@router.post("/agent/run/legacy", summary="Execute agent (legacy)", response_model=AgentResult)
def run_agent_legacy(request: Request, body: AgentRunRequest) -> AgentResult:
    """Execute the default agent with the provided input (legacy endpoint)."""

    request_id = REQUEST_ID_CTX_VAR.get()

    return _legacy_runtime.run(
        input_text=body.input_text,
        request_id=request_id,
        user_id=body.user_id,
        client_id=body.client_id,
        channel=body.channel,
        metadata=body.metadata,
    )


@router.post("/agent/run", summary="Execute agent - PR-022", response_model=RuntimeResult)
def run_agent_v2(request: Request, body: RuntimeRequest) -> RuntimeResult:
    """Execute agent using PR-022 runtime skeleton contract."""

    ctx = RuntimeContext(
        agent=body.agent,
        input=body.input,
        trace_id=body.meta.trace_id,
        mode=body.meta.mode,
        meta=body.meta.model_dump(),
    )

    return _runtime.run(ctx)
