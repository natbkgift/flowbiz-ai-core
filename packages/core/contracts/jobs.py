"""Job envelope contract schema."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class JobEnvelope(BaseModel):
    """Schema-only job envelope for cross-service communication."""

    model_config = ConfigDict(frozen=True)

    job_id: str
    job_type: str
    payload: dict[str, Any]
    trace_id: str | None = None
    created_at: str | None = None
