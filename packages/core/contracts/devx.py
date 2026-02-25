"""Developer experience contracts (DX phase roadmap).

This module accumulates contracts/stubs for PR-102+ developer experience work.
Current contents:
- PR-102: Local dev kit
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ── PR-102: Local dev kit ────────────────────────────────────────────────

DevServiceType = Literal["api", "worker", "db", "cache", "mock", "observability"]
DevCheckStatus = Literal["pass", "warn", "fail"]


class LocalDevServiceSpec(BaseModel):
    """Service entry in a local development kit plan."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    service_name: str
    service_type: DevServiceType
    command: str = ""
    required: bool = True
    ports: list[int] = Field(default_factory=list)
    env_keys: list[str] = Field(default_factory=list)
    notes: str = ""


class LocalDevCheck(BaseModel):
    """Validation check result for local developer setup readiness."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    check_name: str
    status: DevCheckStatus = "pass"
    message: str = ""
    remediation: str = ""


class LocalDevKitPlan(BaseModel):
    """Contract describing a local dev kit composition and readiness checks."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kit_id: str
    profile: Literal["minimal", "default", "full"] = "default"
    services: list[LocalDevServiceSpec] = Field(default_factory=list)
    checks: list[LocalDevCheck] = Field(default_factory=list)
    docs_refs: list[str] = Field(default_factory=list)


def summarize_local_dev_kit(plan: LocalDevKitPlan) -> dict[str, int | str]:
    """Return deterministic summary counters for a local dev kit plan."""

    required_services = sum(1 for service in plan.services if service.required)
    checks_failed = sum(1 for check in plan.checks if check.status == "fail")
    checks_warn = sum(1 for check in plan.checks if check.status == "warn")
    return {
        "kit_id": plan.kit_id,
        "profile": plan.profile,
        "service_count": len(plan.services),
        "required_service_count": required_services,
        "check_count": len(plan.checks),
        "check_fail_count": checks_failed,
        "check_warn_count": checks_warn,
    }
