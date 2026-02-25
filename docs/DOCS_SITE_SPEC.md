# Docs Site Spec (PR-106)

## Status

Docs-only specification in `flowbiz-ai-core`.

Actual docs site implementation is **out of scope** for core and should live in a dedicated docs/web repository.

## Goals

- Publish core documentation with versioned content
- Render API/contract reference pages generated from core docs/contracts
- Support search, navigation, and migration guides
- Keep core repo as canonical source for technical content

## Non-Goals (in this repo)

- Frontend implementation (Next.js/Vite/React/etc.)
- Hosting/CDN/deploy configuration
- Analytics, auth, or UI styling implementation

## Content Sources

- `docs/*.md` (guides, ADRs, runbooks, policies)
- `docs/contracts/**` (contract docs + stubs/examples)
- generated API reference (platform/docs tooling may derive from OpenAPI)

## Suggested External Repo Responsibilities

- site framework and theme
- content ingestion/build pipeline
- version switcher
- search index generation
- deployment/hosting config

## Integration Contract (high level)

- Pull Markdown content from tagged core releases
- Build docs artifacts in docs-site repo CI
- Publish per-version docs alongside `latest`

## Notes

This PR intentionally does **not** add UI code, static assets, or deploy automation to `flowbiz-ai-core`.
