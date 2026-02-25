# Contract Package (Schema-only)

This document defines the `packages/core/contracts` package as a **schema-only boundary** for cross-repo data exchange.

## Purpose

`packages/core/contracts` exists to provide immutable, transport-agnostic Pydantic models that can be safely shared across FlowBiz repositories.

## Rules

- Contracts are data-only models (no execution or orchestration logic).
- Models must be immutable (`frozen=True`) and reject unknown fields (`extra="forbid"`).
- Contracts must not import transport/framework concerns (for example FastAPI).
- Platform/client-specific implementations must live outside this repository.

## Current contracts

- `HealthResponse` (`packages/core/contracts/health.py`)
- `RuntimeMeta` (`packages/core/contracts/meta.py`)
- `JobEnvelope` (`packages/core/contracts/jobs.py`)
- Tool registry contracts (`packages/core/contracts/tool_registry.py`)

## Boundaries

In-scope for this package:
- Contract schemas
- Contract-level validation constraints
- Serialization/deserialization tests

Out-of-scope for this package:
- API endpoint implementation
- Tool execution implementation
- Deploy/runtime integration

## Integration note

Version pinning and downstream integration guidance are documented in `docs/contracts/VERSION_PINNING_AND_INTEGRATION.md`.
