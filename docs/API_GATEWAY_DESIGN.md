# PR-044.14: api.flowbiz.cloud — Public API Gateway (Docs-Only)

> **Scope:** FORBIDDEN in flowbiz-ai-core (platform infrastructure).
> This document describes the design intent; implementation belongs in the platform/deployment repo.

## Overview

`api.flowbiz.cloud` is the public-facing API gateway that proxies requests to the core AI runtime. It is responsible for:

- **TLS termination** — managed by the platform reverse proxy (nginx / Cloudflare)
- **Authentication enforcement** — validates API keys using the contract from PR-044.11
- **Rate limiting** — enforces policies from PR-044.13
- **Request routing** — maps `/v1/*` to the internal core API
- **CORS policy** — configured per-domain at the gateway level

## Why This Is Out of Scope

Per `docs/SCOPE.md`, production ingress routing, WAF/CDN configuration, and platform-wide authentication dashboards are **forbidden** in flowbiz-ai-core.

The core repo provides:
- Auth contracts (`packages/core/contracts/auth.py`)
- Rate limit contracts and in-memory stub
- Health/meta endpoints for the gateway to health-check

The platform repo should:
- Configure nginx/Caddy/Traefik for `api.flowbiz.cloud`
- Wire the `APIKeyValidatorProtocol` to a real key store
- Deploy rate limiting backed by Redis
- Manage TLS certificates

## Integration Pattern

```
Internet → api.flowbiz.cloud (platform nginx)
         → Auth middleware (reads APIKeyInfo)
         → Rate limiter (Redis-backed)
         → Core API (flowbiz-ai-core /v1/*)
```

## Contracts Available in Core

| Contract | Module | Purpose |
|----------|--------|---------|
| `APIKeyInfo` | `contracts/auth.py` | Key metadata after validation |
| `APIKeyValidationResult` | `contracts/auth.py` | Allow/deny with reason |
| `RateLimitPolicy` | `contracts/auth.py` | Policy definition |
| `RateLimitResult` | `contracts/auth.py` | Check outcome |

## Next Steps (Platform Repo)

1. Create `api.flowbiz.cloud` nginx vhost
2. Wire API key validation to PostgreSQL/Vault
3. Deploy Redis-backed rate limiter
4. Add Cloudflare DNS + TLS
5. Monitor via observability hooks (PR-051+)
