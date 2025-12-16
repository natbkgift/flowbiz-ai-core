"""Minimal FastAPI application entrypoint for FlowBiz AI Core."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(title="FlowBiz AI Core", version="0.0.0")

    @app.get("/", summary="Root placeholder")
    async def read_root() -> dict[str, str]:
        return {"message": "FlowBiz AI Core API"}

    return app


app = create_app()
