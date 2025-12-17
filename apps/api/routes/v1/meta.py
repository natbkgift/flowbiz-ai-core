from __future__ import annotations

"""Versioned metadata endpoints."""

from fastapi import APIRouter

from packages.core import get_settings

settings = get_settings()

router = APIRouter(prefix="/v1")


@router.get("/meta", summary="Service metadata")
def get_meta() -> dict[str, str]:
    """Return basic service metadata."""

    return {"service": settings.name, "env": settings.env}
