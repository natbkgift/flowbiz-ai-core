"""Minimal FastAPI application entrypoint for FlowBiz AI Core."""

from fastapi import FastAPI

from packages.core import get_settings

settings = get_settings()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(title=settings.name)

    @app.get("/", summary="Root placeholder")
    async def read_root() -> dict[str, str]:
        return {"message": f"{settings.name} API"}

    return app


app = create_app()
