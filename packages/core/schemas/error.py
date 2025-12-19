"""Schemas for standardized error responses."""

from __future__ import annotations

from .base import BaseSchema


class ErrorPayload(BaseSchema):
    """Details about an error response."""

    code: str
    message: str
    request_id: str
    details: list[str] | None = None


class ErrorResponse(BaseSchema):
    """Standardized error response wrapper."""

    error: ErrorPayload
