"""Tests for organization & billing contracts — PR-061 to PR-070."""

from __future__ import annotations

from packages.core.contracts.billing import (
    BillingAccount,
    BillingWebhookPayload,
    CostEntry,
    CostReport,
    InMemoryOrgStore,
    InMemoryUsageStore,
    InvoiceEvent,
    Organization,
    PlanDefinition,
    Project,
    QuotaCheckResult,
    QuotaPolicy,
    StubQuotaChecker,
    UsageRecord,
    UsageSummary,
)


class TestOrganization:
    def test_schema(self) -> None:
        org = Organization(org_id="org-1", name="Acme Corp", owner_email="a@b.com")
        assert org.org_id == "org-1"
        assert org.name == "Acme Corp"

    def test_frozen(self) -> None:
        org = Organization(org_id="x", name="X")
        try:
            org.name = "Y"  # type: ignore[misc]
            assert False
        except Exception:
            pass


class TestProject:
    def test_schema(self) -> None:
        p = Project(project_id="proj-1", org_id="org-1", name="Main")
        assert p.project_id == "proj-1"
        assert p.org_id == "org-1"


class TestUsageRecord:
    def test_schema(self) -> None:
        u = UsageRecord(org_id="o1", resource="api_calls", quantity=100, unit="request")
        assert u.quantity == 100
        assert u.unit == "request"


class TestUsageSummary:
    def test_schema(self) -> None:
        s = UsageSummary(
            org_id="o1",
            period_start=1.0,
            period_end=2.0,
            total_by_resource={"api_calls": 500},
        )
        assert s.total_by_resource["api_calls"] == 500


class TestQuotaPolicy:
    def test_schema(self) -> None:
        q = QuotaPolicy(org_id="o1", resource="api_calls", limit=1000, unit="request")
        assert q.enforcement == "soft"
        assert q.period_seconds == 86400


class TestQuotaCheckResult:
    def test_allowed(self) -> None:
        r = QuotaCheckResult(allowed=True, current_usage=50, limit=100, remaining=50)
        assert r.allowed


class TestBillingAccount:
    def test_defaults(self) -> None:
        b = BillingAccount(org_id="o1")
        assert b.status == "trial"
        assert b.plan_id == ""


class TestPlanDefinition:
    def test_schema(self) -> None:
        p = PlanDefinition(
            plan_id="pro",
            tier="pro",
            name="Pro Plan",
            price_monthly_cents=4900,
            included_requests=50000,
            features=("priority_support", "advanced_analytics"),
        )
        assert p.tier == "pro"
        assert p.price_monthly_cents == 4900
        assert len(p.features) == 2


class TestInvoiceEvent:
    def test_schema(self) -> None:
        ie = InvoiceEvent(
            invoice_id="inv-1", org_id="o1", status="paid", amount_cents=4900
        )
        assert ie.status == "paid"
        assert ie.currency == "USD"


class TestCostEntry:
    def test_schema(self) -> None:
        ce = CostEntry(
            org_id="o1",
            resource="tokens",
            quantity=10000,
            unit_cost_cents=0.01,
            total_cost_cents=100.0,
            period_start=1.0,
            period_end=2.0,
        )
        assert ce.total_cost_cents == 100.0


class TestCostReport:
    def test_empty(self) -> None:
        cr = CostReport(org_id="o1")
        assert cr.entries == ()
        assert cr.total_cents == 0.0


class TestBillingWebhookPayload:
    def test_schema(self) -> None:
        p = BillingWebhookPayload(
            event="invoice.paid", org_id="o1", data={"amount": 49}
        )
        assert p.event == "invoice.paid"


class TestInMemoryOrgStore:
    def test_crud(self) -> None:
        store = InMemoryOrgStore()
        org = Organization(org_id="o1", name="Test")
        store.create(org)
        assert store.get("o1") is not None
        assert store.get("o1").name == "Test"
        assert len(store.list_all()) == 1

    def test_not_found(self) -> None:
        store = InMemoryOrgStore()
        assert store.get("nope") is None

    def test_clear(self) -> None:
        store = InMemoryOrgStore()
        store.create(Organization(org_id="o1", name="T"))
        store.clear()
        assert store.list_all() == []


class TestInMemoryUsageStore:
    def test_record_and_filter(self) -> None:
        store = InMemoryUsageStore()
        store.record(
            UsageRecord(org_id="o1", resource="api", quantity=1, unit="request")
        )
        store.record(
            UsageRecord(org_id="o2", resource="api", quantity=2, unit="request")
        )
        assert len(store.records_for("o1")) == 1
        assert len(store.records_for("o2")) == 1

    def test_clear(self) -> None:
        store = InMemoryUsageStore()
        store.record(UsageRecord(org_id="o1", resource="x", quantity=1, unit="request"))
        store.clear()
        assert store.records_for("o1") == []


class TestStubQuotaChecker:
    def test_always_allows(self) -> None:
        checker = StubQuotaChecker()
        result = checker.check("o1", "api", 9999)
        assert result.allowed
        assert result.remaining == float("inf")
