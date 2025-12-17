from __future__ import annotations

"""Minimal FastAPI application entrypoint for FlowBiz AI Core."""

import logging
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from apps.api.middleware import RequestIdMiddleware, RequestLoggingMiddleware
from packages.core import build_error_response, get_logger, get_settings

settings = get_settings()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(title=settings.name)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIdMiddleware)

    @app.on_event("startup")
    async def configure_logging() -> None:
        app.state.logger = get_logger("flowbiz.api")
        app.state.logger.info("Logger initialized")

    def _log_error(status_code: int, code: str, message: str) -> None:
        logger = getattr(app.state, "logger", get_logger("flowbiz.api"))
        level = logging.ERROR if status_code >= 500 else logging.WARNING
        logger.log(level, "request error", extra={"status": status_code, "code": code, "message": message})

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException):
        status_code = exc.status_code
        code = f"HTTP_{status_code}"
        message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        _log_error(status_code, code, message)
        return JSONResponse(status_code=status_code, content=build_error_response(code, message))

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        status_code = 422
        code = "HTTP_422"
        message = "Validation Error"
        _log_error(status_code, code, message)
        return JSONResponse(status_code=status_code, content=build_error_response(code, message))

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(request: Request, exc: Exception):
        status_code = 500
        code = "HTTP_500"
        message = "Internal Server Error"
        logger = getattr(app.state, "logger", get_logger("flowbiz.api"))
        logger.error(
            "request error",
            extra={"status": status_code, "code": code, "message": message},
            exc_info=exc,
        )
        return JSONResponse(status_code=status_code, content=build_error_response(code, message))

    @app.get("/", summary="Root placeholder")
    async def read_root() -> dict[str, str]:
        return {"message": f"{settings.name} API"}

    @app.get("/log", summary="Emit a log message for diagnostics")
    async def log_example() -> dict[str, str]:
        app.state.logger.info("Logging from request")
        return {"message": "logged"}

    @app.get("/echo-int", summary="Echo an integer value")
    async def echo_int(value: int) -> dict[str, int]:
        return {"value": value}

    if os.getenv("APP_ENV") == "test":

        @app.get("/__test__/raise", summary="Trigger an internal error for testing", include_in_schema=False)
        async def raise_test_error() -> None:
            raise RuntimeError("Intentional test error")

    return app


app = create_app()
