"""Custom FastAPI middleware implementations."""

from __future__ import annotations

import uuid

import logging
from time import perf_counter

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from packages.core.logging import REQUEST_ID_CTX_VAR, get_logger


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


class RequestLoggingMiddleware:
    """Log a single structured line for each completed request."""

    def __init__(self, app: ASGIApp):
        self.app = app
        self.logger = get_logger(__name__)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = perf_counter()
        status_code: int | None = None

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = int((perf_counter() - start_time) * 1000)
            status = status_code or 500

            if status >= 500:
                level = logging.ERROR
            elif status >= 400:
                level = logging.WARNING
            else:
                level = logging.INFO

            self.logger.log(
                level,
                "request completed",
                extra={
                    "method": scope.get("method"),
                    "path": scope.get("path"),
                    "status": status,
                    "duration_ms": duration_ms,
                    "request_id": REQUEST_ID_CTX_VAR.get(),
                },
            )
            )
