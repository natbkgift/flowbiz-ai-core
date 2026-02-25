# Version Pinning & Integration Notes

This document defines how downstream repositories should consume `flowbiz-ai-core` safely.

## 1) Package Pinning Policy

- **Production services:** pin exact versions (`==`) for deterministic deployments.
- **Pre-production experiments:** may pin compatible minor range (`~=x.y`) only with explicit approval.
- **Never use floating latest** in production (`>=` without upper bound, or no pin).

Examples:

```txt
flowbiz-ai-core==0.0.0
```

```txt
flowbiz-ai-core~=0.3
```

## 2) Compatibility Expectations

- Patch version updates are expected to be backward compatible.
- Minor version updates may add fields and new optional contracts.
- Major version updates may include breaking contract changes and require migration work.

If a breaking contract change is introduced, downstream repos must update with a tested migration plan before rollout.

## 3) Integration Rules for Downstream Repos

- Import only from documented contract modules under `packages.core.contracts`.
- Treat contracts as immutable boundaries: producers and consumers must both validate against the same schema version.
- Keep platform/client-specific logic outside `flowbiz-ai-core` (see `docs/SCOPE.md`).

Recommended import style:

```python
from packages.core.contracts import JobEnvelope, RuntimeMeta
```

## 4) Upgrade Workflow

1. Update pin in dependency file (`requirements.txt` or equivalent).
2. Run full test suite in consumer repo.
3. Validate serialization/deserialization paths for impacted contracts.
4. Roll out in staging before production.
5. Record upgrade note in consumer changelog/ops log.

## 5) Non-Goals

- This document does not define package publishing automation.
- This document does not introduce deploy/runtime integration.
- This document does not change core API behavior.
