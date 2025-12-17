from __future__ import annotations

"""Health check endpoint for FlowBiz AI Core."""

from fastapi import APIRouter

from packages.core.services import MetaService

meta_service = MetaService()

router = APIRouter()


@router.get("/healthz", summary="Health check")
def health_check() -> dict[str, str]:
    """Return service health information."""

    meta = meta_service.get_meta()
    return {"status": "ok", "service": meta["service"], "version": meta["version"]}
