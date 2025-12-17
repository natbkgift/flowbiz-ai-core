from __future__ import annotations

"""Versioned metadata endpoints."""

from fastapi import APIRouter

from packages.core.services import MetaService

meta_service = MetaService()

router = APIRouter(prefix="/v1")


@router.get("/meta", summary="Service metadata")
def get_meta() -> dict[str, str]:
    """Return basic service metadata."""

    return meta_service.get_meta()
