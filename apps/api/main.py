from __future__ import annotations

"""Minimal FastAPI application entrypoint for FlowBiz AI Core."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from apps.api.middleware import RequestIdMiddleware, RequestLoggingMiddleware
from apps.api.routes.health import router as health_router
from apps.api.routes.v1.meta import router as meta_v1_router
from packages.core import build_error_response, get_logger, get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.logger = get_logger("flowbiz.api")
        app.state.logger.info("Logger initialized")
        try:
            yield
        finally:
            # No teardown actions required currently.
            pass

    app = FastAPI(title=settings.name, lifespan=lifespan)

    # innermost
    app.add_middleware(RequestLoggingMiddleware)

    # middle
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        allow_credentials=settings.cors_allow_credentials,
    )

    # outermost
    app.add_middleware(RequestIdMiddleware)

    def _log_error(status_code: int, code: str, message: str) -> None:
        logger = getattr(app.state, "logger", get_logger("flowbiz.api"))
        level = logging.ERROR if status_code >= 500 else logging.WARNING
        logger.log(level, "request error", extra={"status": status_code, "code": code, "error_message": message})

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
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
            extra={"status": status_code, "code": code, "error_message": message},
            exc_info=exc,
        )
        return JSONResponse(status_code=status_code, content=build_error_response(code, message))

    app.include_router(health_router)
    app.include_router(meta_v1_router)

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
