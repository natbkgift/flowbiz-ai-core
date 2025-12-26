"""Runtime request schema."""

from __future__ import annotations

from pydantic import Field

from packages.core.schemas.base import BaseSchema


class RuntimeRequestMeta(BaseSchema):
    """Metadata for runtime request."""

    trace_id: str | None = None
    mode: str = "dev"


class RuntimeRequest(BaseSchema):
    """Request schema for agent runtime execution."""

    agent: str
    input: str
    meta: RuntimeRequestMeta = Field(default_factory=RuntimeRequestMeta)
