# Admin UI Spec (PR-118)

## Status

Docs-only(out-of-scope) in `flowbiz-ai-core`.

Admin UI implementation is a frontend/platform responsibility and must be built in a separate web/admin repository.

## Goals

- Provide operational/admin views for platform-managed features
- Expose safe controls for tenant/project settings (implemented outside core)
- Visualize core-derived data/contracts using platform APIs

## Non-Goals (in core)

- UI components/pages/routes
- authentication/session/role UI
- deployment/hosting/frontend build config

## Core Touchpoints (for external implementation)

- Core API endpoints and contracts
- `docs/TOOL_PERMISSIONS.md`, `docs/PR_LOG.md`, `docs/PR_STATE.md`
- Contract examples under `docs/contracts/stubs/**`
