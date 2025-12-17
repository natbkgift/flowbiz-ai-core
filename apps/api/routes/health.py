from __future__ import annotations

"""Health check endpoint for FlowBiz AI Core."""

import os

from fastapi import APIRouter

from packages.core import get_settings

settings = get_settings()

router = APIRouter()


@router.get("/healthz", summary="Health check")
async def health_check() -> dict[str, str]:
    """Return service health information."""

    version = os.getenv("APP_VERSION") or "dev"
    return {"status": "ok", "service": settings.name, "version": version}
