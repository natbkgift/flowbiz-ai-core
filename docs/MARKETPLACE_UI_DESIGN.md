# Marketplace UI API Design — PR-080

> **Scope:** docs-only — UI implementation is FORBIDDEN per SCOPE.md.

## Purpose

The marketplace UI provides a browsable catalog of agents and tools
for installation into projects.  The UI lives in a separate project;
this document defines the API endpoints it would consume from Core
contracts.

## API Endpoints (consumed by UI, not implemented in core)

| Method | Path | Description | Contract |
|--------|------|-------------|----------|
| GET | /marketplace/search | Search/filter agents | `MarketplaceSearchResult` |
| GET | /marketplace/agents/{id} | Agent details | `AgentManifest` |
| GET | /marketplace/agents/{id}/versions | Version history | `AgentVersion[]` |
| GET | /marketplace/agents/{id}/ratings | Rating summary | `AgentRatingSummary` |
| POST | /marketplace/agents/{id}/rate | Submit rating | `AgentRating` |
| POST | /marketplace/agents/{id}/install | Install to project | `AgentInstallation` |
| PUT | /marketplace/agents/{id}/update | Update version | `AgentUpdateRequest` |
| DELETE | /marketplace/agents/{id}/uninstall | Uninstall | — |
| GET | /marketplace/agents/{id}/usage | Usage analytics | `AgentUsageMetrics` |

## UI Panels

1. **Browse/Search** — grid of agent cards with filters (category, tags, rating)
2. **Agent Detail** — description, screenshots, version history, reviews
3. **Install Flow** — version select, config form (from `config_schema`), permissions review
4. **My Agents** — installed agents per project, update available indicators
5. **Publisher Dashboard** — publish new agents, usage analytics, ratings

## Implementation Notes

- All contracts are defined in `packages/core/contracts/marketplace.py`
- UI project should import contracts from the published SDK
- Authentication via API key (see `packages/core/contracts/auth.py`)
