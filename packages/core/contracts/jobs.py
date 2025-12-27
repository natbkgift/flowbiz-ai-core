"""Job envelope contract schema."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class JobEnvelope(BaseModel):
    """
    Schema-only job envelope for cross-service communication.

    The `payload` field contains job-specific data whose concrete schema is
    determined by the `job_type`. It is expected to be a JSON-serializable
    mapping (e.g. keys as strings and values as basic types, lists, or
    nested mappings) that conforms to the contract agreed for the given
    `job_type` between producer and consumer services.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    job_id: str
    job_type: str
    payload: dict[str, Any] = Field(
        ...,
        description=(
            "Job-specific data whose structure is defined by the `job_type`. "
            "Must be JSON-serializable and conform to the contract agreed "
            "between producer and consumer services for that job type."
        ),
    )
    trace_id: str | None = None
    created_at: str | None = None
