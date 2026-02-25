"""API v2 placeholder router — PR-045.

Demonstrates versioned API pattern: v1 endpoints remain stable while
v2 can introduce breaking changes or new schemas.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/v2")


@router.get("/meta", summary="Service metadata (v2)")
def get_meta_v2() -> dict[str, Any]:
    """Return v2 metadata — extends v1 with additional fields."""
    from packages.core.services import MetaService

    meta = MetaService().get_meta()
    return {
        **meta,
        "api_version": "v2",
        "capabilities": [
            "agent_run",
            "tool_registry",
            "workflow_contracts",
            "auth_contracts",
        ],
    }
