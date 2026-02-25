# Multi-Tenant Deploy Spec (PR-119)

## Status

Docs-only(out-of-scope) in `flowbiz-ai-core`.

Multi-tenant deployment architecture and execution are platform/infra responsibilities and must not be implemented in core.

## Safety Constraints (Core Repo)

- No deploy execution from this PR
- No VPS mutations
- No system nginx changes
- No `.github` / `docker-compose*.yml` / `nginx/**` changes

## Goal (Platform-Side)

Define how platform infrastructure should deploy and isolate multiple tenants while consuming shared core contracts/runtime.

## Core vs Platform Ownership

- Core (`flowbiz-ai-core`)
  - contracts, schemas, runtime primitives, docs
  - no tenant routing/deploy orchestration

- Platform/Infra repos
  - tenant routing
  - per-tenant config/secrets
  - deployment pipelines
  - observability, isolation, scaling policies

## Required Platform Design Topics (external implementation)

- tenant isolation boundaries (network, data, config)
- per-tenant secrets and rotation
- routing and domain management
- deployment rollout/rollback strategy
- quota and rate limiting enforcement
- operational runbooks and incident response

## References

- `docs/CODEX_AGENT_BEHAVIOR_LOCK.md`
- `docs/SCOPE.md`
- `docs/GUARDRAILS.md`

## Note

If implementation work is needed, it must be done in a platform/infra repository with explicit deploy authorization (`DEPLOY`) and checklist completion.
