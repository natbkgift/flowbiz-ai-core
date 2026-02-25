# API Playground Spec (PR-107)

## Status

Docs-only(out-of-scope) specification in `flowbiz-ai-core`.

A real API playground is a UI application and must be implemented in a platform/web/docs repository, not in core.

## Goals

- Interactive exploration of FlowBiz AI Core HTTP endpoints
- Request/response examples for `/v1/*` and `/v2/*`
- Safe example payload templates
- Developer onboarding and debugging aid

## Non-Goals (in core)

- Browser UI implementation
- API proxy hosting/auth/session management
- Rate-limit bypass or production credential handling

## Required Features (for external implementation)

- OpenAPI import (or generated endpoint catalog)
- Environment selector (`local`, `staging`, `production`) with warnings
- Example requests for agent run/tools/health/meta endpoints
- Redaction of secrets and unsafe headers in shared snippets
- Copyable `curl` output

## Security / Safety Notes

- Never embed production secrets in the playground UI
- Require explicit warnings for production target usage
- Sanitize stored request history

## Integration with Core

- Consume `docs/PR_LOG.md`, OpenAPI docs, and contract examples as source material
- Do not require core repo to host the playground runtime
