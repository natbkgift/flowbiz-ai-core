# Health Dashboard Design — PR-057

> **Scope:** docs-only — UI implementation is FORBIDDEN per SCOPE.md.

## Purpose

A health dashboard provides at-a-glance operational visibility across
FlowBiz AI Core services.  The dashboard itself lives in a separate
UI project; this document defines what Core **exposes** for consumption.

## Data Sources (provided by Core)

| Source | Endpoint / Contract | Notes |
|--------|---------------------|-------|
| Health probe | `GET /healthz` | Basic liveness |
| Agent health | `GET /v1/agent/health` | Registered agents + tools count |
| Metrics | `MetricsSnapshot` contract | Counter / gauge / histogram samples |
| Tracing | `TraceExport` contract | Span collector export |
| Error aggregation | `ErrorAggregateSnapshot` | Grouped error counts |
| Slow queries | `SlowQuerySnapshot` | Operations exceeding threshold |
| Request analytics | `RequestAnalyticsSnapshot` | p95, avg, path breakdown |
| Uptime | `UptimeSnapshot` | Per-check status + overall |
| Alerts | `AlertEvent` list | Firing / resolved events |

## Recommended Dashboard Panels

1. **Service Status** — traffic-light from `/healthz` + uptime checks
2. **Request Rate** — counter metric `http_requests_total`
3. **Error Rate** — `error_count / total_requests` from analytics
4. **Latency Distribution** — histogram / p95 from analytics
5. **Active Alerts** — firing alert events
6. **Slow Queries** — top-N by duration
7. **Agent Registry** — registered agents / tools from `/v1/agent/health`

## Implementation Notes

- Dashboard **reads** from Core contracts / endpoints; it never writes.
- Use SSE or polling (60 s) for refresh.
- The dashboard project should be a separate repository (e.g., `flowbiz-dashboard`).
