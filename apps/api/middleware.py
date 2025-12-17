"""Custom FastAPI middleware implementations."""

from __future__ import annotations

import uuid
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from packages.core.logging import REQUEST_ID_CTX_VAR


def _generate_request_id() -> str:
    """Create a new UUID4 request identifier."""

    return str(uuid.uuid4())


def _validate_request_id(value: str | None) -> str:
    """Return a valid request ID, falling back to a generated UUID4."""

    if not value:
        return _generate_request_id()

    try:
        parsed = uuid.UUID(value)
    except ValueError:
        return _generate_request_id()

    return str(parsed)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach and propagate request IDs for each request."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request_id = _validate_request_id(request.headers.get("X-Request-ID"))
        token = REQUEST_ID_CTX_VAR.set(request_id)

        try:
            response = await call_next(request)
        finally:
            REQUEST_ID_CTX_VAR.reset(token)

        response.headers["X-Request-ID"] = request_id
        return response
