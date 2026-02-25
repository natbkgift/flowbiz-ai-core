"""Organization & billing contracts — PR-061 to PR-070.

ALL items in this module are FORBIDDEN per SCOPE.md (billing, payments,
invoicing, cost attribution, usage dashboards).  This file provides
**contracts and stubs only** so platform code can depend on stable
interfaces without pulling implementation into core.

PR-061: Organization model
PR-062: Project / workspace
PR-063: Usage tracking
PR-064: Quota system
PR-065: Billing abstraction
PR-066: Plan tiers
PR-067: Invoice events
PR-068: Cost attribution
PR-069: Usage dashboard (docs-only — UI forbidden)
PR-070: Billing webhooks
"""

from __future__ import annotations

import time
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# PR-061 — Organization model
# ---------------------------------------------------------------------------


class Organization(BaseModel):
    """Top-level tenant / customer entity."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    org_id: str
    name: str
    owner_email: str = ""
    created_at: float = Field(default_factory=time.time)
    metadata: dict[str, str] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# PR-062 — Project / workspace
# ---------------------------------------------------------------------------


class Project(BaseModel):
    """Workspace / project within an organization."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    project_id: str
    org_id: str
    name: str
    description: str = ""
    created_at: float = Field(default_factory=time.time)


# ---------------------------------------------------------------------------
# PR-063 — Usage tracking
# ---------------------------------------------------------------------------

UsageUnit = Literal["request", "token", "second", "byte"]


class UsageRecord(BaseModel):
    """Single usage event."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    org_id: str
    project_id: str = ""
    resource: str
    quantity: float
    unit: UsageUnit
    timestamp: float = Field(default_factory=time.time)


class UsageSummary(BaseModel):
    """Aggregated usage over a period."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    org_id: str
    period_start: float
    period_end: float
    total_by_resource: dict[str, float] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# PR-064 — Quota system
# ---------------------------------------------------------------------------

QuotaEnforcement = Literal["soft", "hard"]


class QuotaPolicy(BaseModel):
    """Resource quota for an organization or project."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    org_id: str
    resource: str
    limit: float
    unit: UsageUnit
    enforcement: QuotaEnforcement = "soft"
    period_seconds: int = 86400  # daily default


class QuotaCheckResult(BaseModel):
    """Result of checking quota before an operation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    allowed: bool
    current_usage: float = 0.0
    limit: float = 0.0
    remaining: float = 0.0
    enforcement: QuotaEnforcement = "soft"


# ---------------------------------------------------------------------------
# PR-065 — Billing abstraction
# ---------------------------------------------------------------------------

BillingStatus = Literal["active", "past_due", "canceled", "trial"]


class BillingAccount(BaseModel):
    """Billing account linked to an organization."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    org_id: str
    status: BillingStatus = "trial"
    plan_id: str = ""
    payment_method_id: str = ""  # opaque reference
    created_at: float = Field(default_factory=time.time)


# ---------------------------------------------------------------------------
# PR-066 — Plan tiers
# ---------------------------------------------------------------------------

PlanTier = Literal["free", "starter", "pro", "enterprise"]


class PlanDefinition(BaseModel):
    """Subscription plan tier definition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    plan_id: str
    tier: PlanTier
    name: str
    price_monthly_cents: int = 0
    included_requests: int = 0
    included_tokens: int = 0
    features: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# PR-067 — Invoice events
# ---------------------------------------------------------------------------

InvoiceStatus = Literal["draft", "open", "paid", "void"]


class InvoiceEvent(BaseModel):
    """Event emitted when an invoice is created, paid, etc."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    invoice_id: str
    org_id: str
    status: InvoiceStatus
    amount_cents: int = 0
    currency: str = "USD"
    timestamp: float = Field(default_factory=time.time)


# ---------------------------------------------------------------------------
# PR-068 — Cost attribution
# ---------------------------------------------------------------------------


class CostEntry(BaseModel):
    """Attributed cost for a specific resource."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    org_id: str
    project_id: str = ""
    resource: str
    quantity: float
    unit_cost_cents: float
    total_cost_cents: float
    period_start: float
    period_end: float


class CostReport(BaseModel):
    """Aggregated cost report."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    org_id: str
    entries: tuple[CostEntry, ...] = ()
    total_cents: float = 0.0
    currency: str = "USD"
    generated_at: float = Field(default_factory=time.time)


# ---------------------------------------------------------------------------
# PR-070 — Billing webhooks
# ---------------------------------------------------------------------------

BillingWebhookEvent = Literal[
    "invoice.created",
    "invoice.paid",
    "subscription.created",
    "subscription.canceled",
    "quota.exceeded",
]


class BillingWebhookPayload(BaseModel):
    """Webhook payload for billing events."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    event: BillingWebhookEvent
    org_id: str
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


# ---------------------------------------------------------------------------
# Stubs — InMemory stores for testing
# ---------------------------------------------------------------------------


class InMemoryOrgStore:
    """Stub organization store."""

    def __init__(self) -> None:
        self._orgs: dict[str, Organization] = {}

    def create(self, org: Organization) -> None:
        self._orgs[org.org_id] = org

    def get(self, org_id: str) -> Organization | None:
        return self._orgs.get(org_id)

    def list_all(self) -> list[Organization]:
        return list(self._orgs.values())

    def clear(self) -> None:
        self._orgs.clear()


class InMemoryUsageStore:
    """Stub usage tracking store."""

    def __init__(self) -> None:
        self._records: list[UsageRecord] = []

    def record(self, entry: UsageRecord) -> None:
        self._records.append(entry)

    def records_for(self, org_id: str) -> list[UsageRecord]:
        return [r for r in self._records if r.org_id == org_id]

    def clear(self) -> None:
        self._records.clear()


class StubQuotaChecker:
    """Always-allow quota checker stub."""

    def check(self, org_id: str, resource: str, quantity: float) -> QuotaCheckResult:
        return QuotaCheckResult(
            allowed=True,
            current_usage=0.0,
            limit=float("inf"),
            remaining=float("inf"),
        )
