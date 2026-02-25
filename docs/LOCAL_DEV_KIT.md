# Local Dev Kit (PR-102)

## Purpose

Define a **core-safe local development kit contract** for running and validating FlowBiz AI Core locally without embedding platform-specific deploy logic in this repository.

This PR intentionally avoids changing:
- `.github/**`
- `docker-compose*.yml`
- `nginx/**`
- VPS/system deployment files

## Scope in Core

In `flowbiz-ai-core`, PR-102 provides:
- contract models for local dev service definitions
- contract models for readiness checks
- deterministic summary helper for tooling/tests
- documentation for how platform repos can map these contracts to actual compose/dev tooling

## Out of Scope (Platform/Infra)

Actual local orchestration implementation belongs to:
- platform repo compose stacks
- devcontainer definitions
- OS-specific scripts (Windows/macOS/Linux)
- secret provisioning

## Contract Summary

Added in `packages/core/contracts/devx.py`:
- `LocalDevServiceSpec`
- `LocalDevCheck`
- `LocalDevKitPlan`
- `summarize_local_dev_kit(plan)`

These contracts are intended to describe a local kit, not execute it.

## Example (contract-level)

```python
from packages.core.contracts.devx import LocalDevKitPlan, LocalDevServiceSpec

plan = LocalDevKitPlan(
    kit_id="core-default",
    services=[
        LocalDevServiceSpec(service_name="api", service_type="api", ports=[8000]),
        LocalDevServiceSpec(service_name="postgres", service_type="db", ports=[5432]),
    ],
)
```

## Integration Notes

- Platform repos can serialize `LocalDevKitPlan` to YAML/JSON and map to compose/dev scripts.
- Core tests validate shape and deterministic summaries only.
- No deploy or runtime infra actions are performed by this PR.
