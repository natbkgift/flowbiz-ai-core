"""Health contract schema."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """Minimal health response schema."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: Literal["ok"]
    service: str
    version: str
