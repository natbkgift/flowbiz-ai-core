"""Versioned metadata endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from packages.core.schemas import MetaResponse
from packages.core.services import MetaService

meta_service = MetaService()

router = APIRouter(prefix="/v1")


@router.get("/meta", summary="Service metadata", response_model=MetaResponse)
def get_meta() -> MetaResponse:
    """Return basic service metadata including version information."""

    return MetaResponse(**meta_service.get_meta())
