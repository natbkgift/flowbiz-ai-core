"""Runtime request schema."""

from __future__ import annotations

from packages.core.schemas.base import BaseSchema


class RuntimeRequestMeta(BaseSchema):
    """Metadata for runtime request."""

    trace_id: str | None = None
    mode: str = "dev"


class RuntimeRequest(BaseSchema):
    """Request schema for agent runtime execution."""

    agent: str
    input: str
    meta: RuntimeRequestMeta | None = None

    def __init__(self, **data):
        """Initialize RuntimeRequest with default meta."""
        if "meta" not in data or data["meta"] is None:
            data["meta"] = RuntimeRequestMeta()
        super().__init__(**data)
