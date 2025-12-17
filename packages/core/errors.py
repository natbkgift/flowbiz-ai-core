"""Standardized error response utilities."""

from __future__ import annotations

import uuid

from .logging import REQUEST_ID_CTX_VAR


def _current_request_id() -> str:
    """Return the current request id from context or generate a new one."""

    return REQUEST_ID_CTX_VAR.get() or str(uuid.uuid4())


def build_error_response(code: str, message: str) -> dict[str, dict[str, str]]:
    """Create a standardized error response payload."""

    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": _current_request_id(),
        }
    }
