"""Schemas for health endpoints."""

from __future__ import annotations

from .base import BaseSchema


class HealthResponse(BaseSchema):
    """Response schema for service health checks."""

    status: str
    service: str
    version: str
