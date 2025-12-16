"""Minimal FastAPI application entrypoint for FlowBiz AI Core."""

from fastapi import FastAPI

from packages.core import get_logger, get_settings

settings = get_settings()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(title=settings.name)

    @app.on_event("startup")
    async def configure_logging() -> None:
        app.state.logger = get_logger("flowbiz.api")
        app.state.logger.info("Logger initialized", extra={"request_id": "-"})

    @app.get("/", summary="Root placeholder")
    async def read_root() -> dict[str, str]:
        return {"message": f"{settings.name} API"}

    return app


app = create_app()
