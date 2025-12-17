"""Minimal FastAPI application entrypoint for FlowBiz AI Core."""

from fastapi import FastAPI

from apps.api.middleware import RequestIdMiddleware, RequestLoggingMiddleware
from packages.core import get_logger, get_settings

settings = get_settings()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(title=settings.name)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

    @app.on_event("startup")
    async def configure_logging() -> None:
        app.state.logger = get_logger("flowbiz.api")
        app.state.logger.info("Logger initialized", extra={"request_id": "-"})

    @app.get("/", summary="Root placeholder")
    async def read_root() -> dict[str, str]:
        return {"message": f"{settings.name} API"}

    @app.get("/log", summary="Emit a log message for diagnostics")
    async def log_example() -> dict[str, str]:
        app.state.logger.info("Logging from request")
        return {"message": "logged"}

    return app


app = create_app()
