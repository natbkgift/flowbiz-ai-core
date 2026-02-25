# Web App Shell Spec (PR-117)

## Status

Docs-only(out-of-scope) in `flowbiz-ai-core`.

Web app shell implementation is a frontend concern and must live in a platform/web UI repository.

## Goals

- Provide shell layout/navigation for AI features
- Integrate with backend APIs and auth (implemented outside core)
- Host feature modules (marketplace, admin, workflows, analytics) via web UI repo

## Non-Goals (in core)

- UI implementation (React/Next.js/etc.)
- frontend routing/state/auth logic
- static assets/design system code
- hosting/deployment configuration

## Core Touchpoints (for external team)

- consume core API/OpenAPI/contract docs
- render examples from `docs/contracts/stubs/**`
- respect personas/tool permission docs when building UX
