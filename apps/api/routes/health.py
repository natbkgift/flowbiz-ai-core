"""Health check endpoint for FlowBiz AI Core."""

from __future__ import annotations

from fastapi import APIRouter

from packages.core.schemas import HealthResponse
from packages.core.services import MetaService

meta_service = MetaService()

router = APIRouter()


@router.get("/healthz", summary="Health check", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return service health information."""

    meta = meta_service.get_meta()
    return HealthResponse(
        status="ok",
        service=meta.get("service"),
        version=meta.get("version"),
    )
