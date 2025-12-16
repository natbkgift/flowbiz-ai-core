"""A lightweight stub implementation of the FastAPI interface.

This stub provides only the minimal surface area needed for local
unit tests and does not attempt to replicate the full FastAPI
framework. It supports registering GET routes and handling requests
via a companion :class:`~fastapi.testclient.TestClient`.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


class FastAPI:
    """Minimal FastAPI-like application container."""

    def __init__(self, *, title: str | None = None, version: str | None = None):
        self.title = title
        self.version = version
        self._routes: dict[tuple[str, str], tuple[Callable[P, R] | Callable[P, Awaitable[R]], str | None]] = {}

    def get(self, path: str, *, summary: str | None = None) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """Decorator used to register a GET route.

        Only the path and handler are stored; route definitions are consumed
        by :class:`fastapi.testclient.TestClient` to handle simulated requests
        in unit tests.
        """

        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            self._routes[("GET", path)] = (func, summary)
            return func

        return decorator

    def route_handler(self, method: str, path: str) -> Callable[P, R] | Callable[P, Awaitable[R]] | None:
        """Retrieve a registered route handler if one exists."""

        route = self._routes.get((method.upper(), path))
        if route is None:
            return None
        handler, _ = route
        return handler


__all__ = ["FastAPI"]
