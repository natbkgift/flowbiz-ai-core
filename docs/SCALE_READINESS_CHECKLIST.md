# Scale Readiness Checklist

> PR-100 — docs-only (final review checklist)

## Purpose

Before going to production at scale, every item below should be assessed.
Use `ScaleReadinessCheck` / `ScaleReadinessReport` contracts in
`packages/core/contracts/performance.py` to track results programmatically.

## Checklist

### Database
- [ ] Connection pooling configured (PgBouncer / pgpool)
- [ ] Read replicas provisioned and lag < 5 s
- [ ] Slow query log enabled, reviewed weekly
- [ ] Index recommendations applied
- [ ] Backup & restore tested

### API Layer
- [ ] Rate limiting enabled per client / endpoint
- [ ] Request timeout configured (< 30 s)
- [ ] Health endpoint excludes heavy checks
- [ ] Graceful shutdown with drain period

### Caching
- [ ] Cache layer configured (Redis / in-memory)
- [ ] Cache invalidation strategy documented
- [ ] Cache hit rate monitored (target ≥ 90 %)

### Queue / Workers
- [ ] Queue backend deployed (Redis, RabbitMQ, SQS, …)
- [ ] Dead-letter queue configured
- [ ] Worker autoscale policy tested
- [ ] Retry / back-off strategy documented

### Networking
- [ ] CDN for static assets
- [ ] Gzip / Brotli compression enabled
- [ ] Keep-alive connections configured
- [ ] TLS 1.3 enforced

### Observability
- [ ] Metrics exported to Prometheus
- [ ] Distributed tracing enabled
- [ ] Alert rules defined for error rate, latency, saturation
- [ ] Incident runbook up to date

### Security
- [ ] Secrets rotated within policy window
- [ ] Audit logging enabled
- [ ] GDPR data-export endpoint tested
- [ ] Penetration test completed or scheduled

### Load Testing
- [ ] Baseline load test run (current RPS)
- [ ] Target RPS load test passed
- [ ] Spike test (2× target) evaluated
- [ ] Soak test (24 h at target) evaluated

## Outcome

| Status | Meaning |
|--------|---------|
| `ready` | All checks pass |
| `needs_work` | One or more items require action |
| `not_assessed` | Item not yet reviewed |

Generate a `ScaleReadinessReport` and store it for audit.
