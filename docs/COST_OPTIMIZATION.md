# Cost Optimization Guide

> PR-099 — docs-only (infrastructure decisions out of scope per SCOPE.md)

## Principles

1. **Right-size first** — measure actual usage before allocating resources.
2. **Scale down as eagerly as you scale up** — set aggressive cool-down on
   scale-down to avoid over-provisioning.
3. **Use spot/preemptible instances** for batch workloads.
4. **Cache aggressively** — every cache hit avoids compute, DB, and network cost.
5. **Monitor per-request cost** — track the cost of a single API call so that
   regressions are visible immediately.

## Recommended Reviews

| Area | Check | Target |
|------|-------|--------|
| Compute | CPU utilisation ≥ 60 % sustained | Right-size or autoscale |
| Storage | Unused volumes / snapshots | Delete or archive |
| Network | Cross-AZ traffic | Co-locate services |
| DB | Idle connections, oversized instances | Connection pooling, downsize |
| Caching | Hit rate ≥ 90 % | Tune TTL, key strategy |

## Tools

- **Cloud provider cost dashboards** (AWS Cost Explorer, GCP Billing, etc.)
- **Prometheus / Grafana** for per-service resource metrics.
- **`packages/core/contracts/performance.py`** — `ResourceUsage` and
  `CostOptimizationSuggestion` contracts for programmatic tracking.

## Process

1. Weekly automated cost report (contracts in `performance.py`).
2. Monthly manual review of top-5 cost drivers.
3. Quarterly right-sizing exercise with autoscale policy tuning.
