"""Base schema definitions for API contracts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema enforcing strict validation and serialization rules."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    def model_dump(self, *args, **kwargs):  # type: ignore[override]
        """Dump model data while excluding ``None`` fields by default."""

        kwargs.setdefault("exclude_none", True)
        return super().model_dump(*args, **kwargs)

    def model_dump_json(self, *args, **kwargs):  # type: ignore[override]
        """Dump model data to JSON while excluding ``None`` fields by default."""

        kwargs.setdefault("exclude_none", True)
        return super().model_dump_json(*args, **kwargs)
