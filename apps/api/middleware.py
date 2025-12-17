"""Custom FastAPI middleware implementations."""

from __future__ import annotations

import uuid

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

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


class RequestIdMiddleware:
    """Attach and propagate request IDs for each request."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        request_id = _validate_request_id(headers.get("X-Request-ID"))
        token = REQUEST_ID_CTX_VAR.set(request_id)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                response_headers = MutableHeaders(scope=message)
                response_headers["X-Request-ID"] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            REQUEST_ID_CTX_VAR.reset(token)
