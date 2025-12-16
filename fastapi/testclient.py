"""A lightweight test client compatible with the local FastAPI stub."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from . import FastAPI


@dataclass
class Response:
    """Represents a simple HTTP-like response."""

    status_code: int
    body: Any

    def json(self) -> Any:  # pragma: no cover - trivial passthrough
        return self.body


class TestClient:
    """Minimal client that dispatches requests to the stub FastAPI app."""

    def __init__(self, app: FastAPI):
        self.app = app

    def get(self, path: str) -> Response:
        handler = self.app.route_handler("GET", path)
        if handler is None:
            return Response(status_code=404, body={"detail": "Not Found"})

        result = handler()
        if asyncio.iscoroutine(result):
            result = asyncio.run(result)

        return Response(status_code=200, body=result)


__all__ = ["TestClient", "Response"]
