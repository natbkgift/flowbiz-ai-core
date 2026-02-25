# Usage Dashboard Design — PR-069

> **Scope:** docs-only — UI implementation is FORBIDDEN per SCOPE.md.

## Purpose

A usage dashboard displays resource consumption, costs, and quota
status to organization admins.  The dashboard itself lives in a
separate UI project; this document defines what Core **exposes**.

## Data Sources (provided by Core contracts)

| Source | Contract | Notes |
|--------|----------|-------|
| Organization | `Organization` | Tenant identity |
| Projects | `Project` | Workspace breakdown |
| Usage records | `UsageRecord` | Per-request/token tracking |
| Usage summary | `UsageSummary` | Aggregated by period |
| Quota status | `QuotaCheckResult` | Current vs. limit |
| Billing account | `BillingAccount` | Plan + status |
| Plan definition | `PlanDefinition` | Tier features |
| Cost report | `CostReport` | Attributed costs |
| Invoices | `InvoiceEvent` | Invoice lifecycle |

## Recommended Panels

1. **Current Period Usage** — bar chart by resource (requests, tokens)
2. **Quota Gauge** — percentage used vs. limit per resource
3. **Cost Breakdown** — pie chart by project / resource
4. **Invoice History** — table of past invoices with status
5. **Plan Details** — current tier, included limits, upgrade CTA
6. **Usage Trend** — line chart over last 30 days

## Implementation Notes

- Dashboard is read-only over Core contracts.
- Separate repo (e.g., `flowbiz-dashboard` or `flowbiz-admin-ui`).
- Polling interval: 5 min for usage, 1 hr for cost reports.
