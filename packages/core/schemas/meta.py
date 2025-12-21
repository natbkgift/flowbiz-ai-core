"""Schemas for metadata endpoints."""

from __future__ import annotations

from .base import BaseSchema


class MetaResponse(BaseSchema):
    """Response schema for service metadata."""

    service: str
    env: str
    version: str
