# Release & Rollback Runbook (Core)

This runbook defines a practical, auditable release process for `flowbiz-ai-core` with explicit version alignment, deployment verification, promotion, and rollback steps.

It is designed to work with:
- `scripts/vps_deploy.ps1`
- `scripts/smoke_prod_api.ps1`
- `scripts/release_preflight.ps1`

## Goals

- Keep **app version** and **release tag** aligned for deployable runtime releases
- Deploy by **commit SHA** (deterministic)
- Promote to stable tag **only after** post-deploy verification passes
- Make rollback a **documented command**, not an improvisation

## Versioning Rules (Core Runtime Releases)

- `pyproject.toml` `[project].version` MUST match:
  - `.env.example` `FLOWBIZ_VERSION`
  - runtime version exposed by `/healthz` and `/v1/meta` after deploy
- Stable release tags use `vX.Y.Z` and MUST point to the exact deployed commit
- Deploy first by commit SHA, then promote by creating/pushing the stable tag after smoke checks pass

## Release Flow (Recommended)

### 1) Prepare version bump and checks (local)

1. Bump version in source (`pyproject.toml`, `.env.example`, runtime/version-related defaults as needed)
2. Run quality gates:
   - `ruff check .`
   - `pytest -q`
3. Run release preflight:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/release_preflight.ps1 -ExpectedTag vX.Y.Z
```

This verifies:
- working tree is clean
- core version values are aligned
- target tag does not already exist locally

### 2) Commit and push

```powershell
git push origin main
```

Record the deployment target commit SHA:

```powershell
git rev-parse --short HEAD
```

### 3) Deploy candidate by commit SHA (not tag yet)

Use a fixed SHA for deterministic deployment:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/vps_deploy.ps1 `
  -RemotePath /opt/flowbiz/flowbiz-ai-core `
  -GitRef <commit-sha> `
  -SourceMode git `
  -ComposeFiles docker-compose.yml docker-compose.prod-api.yml `
  -HealthMode host `
  -HealthUrlLocal http://127.0.0.1:8000/healthz `
  -PublicHealthUrl https://flowbiz.cloud/api/healthz
```

If the VPS checkout is known to be dirty (e.g., previous `upload` deploys), use:

```powershell
-ResetRemoteGitWorkingTree
```

This keeps the deploy fail-fast by default, and only cleans the remote git tree when explicitly requested.

### 4) Run post-deploy smoke test (read-only)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/smoke_prod_api.ps1 `
  -BaseUrl https://flowbiz.cloud/api `
  -TimeoutSec 15 `
  -Retries 2
```

Required pass conditions:
- `/healthz` = `200`
- `/v1/meta` = `200`
- `/openapi.json` = `200`
- versions reported by `healthz`, `meta`, and `openapi.info.version` match the intended release version

### 5) Promote to stable release tag (after verification)

Only after deployment + smoke checks pass:

```powershell
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

This tag is the **promotion marker** for the verified production release.

## Rollback Flow

### Option A (Preferred): Roll back to previous stable tag

Redeploy the last known-good tag/commit using the same deploy script:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/vps_deploy.ps1 `
  -RemotePath /opt/flowbiz/flowbiz-ai-core `
  -GitRef vX.Y.Z `
  -SourceMode git `
  -ComposeFiles docker-compose.yml docker-compose.prod-api.yml `
  -HealthMode host `
  -HealthUrlLocal http://127.0.0.1:8000/healthz `
  -PublicHealthUrl https://flowbiz.cloud/api/healthz
```

Then re-run smoke test:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/smoke_prod_api.ps1 -BaseUrl https://flowbiz.cloud/api
```

### Option B: Roll back to explicit commit SHA

Use when the previous stable SHA is known but a tag is not yet available:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/vps_deploy.ps1 `
  -RemotePath /opt/flowbiz/flowbiz-ai-core `
  -GitRef <previous-good-sha> `
  -SourceMode git `
  -ComposeFiles docker-compose.yml docker-compose.prod-api.yml `
  -HealthMode host `
  -HealthUrlLocal http://127.0.0.1:8000/healthz `
  -PublicHealthUrl https://flowbiz.cloud/api/healthz
```

## Operational Notes

- `scripts/vps_deploy.ps1` now fails if:
  - `ssh`, `scp`, or `git` commands exit non-zero
  - remote deploy output does not include the expected success marker
- `SourceMode=upload` is useful for local unpushed changes, but can leave the VPS checkout in a dirty git state
- Prefer `SourceMode=git` for normal release/promotion flows

## Incident / Audit Trail

After release or rollback:
- record the deployed SHA and tag (if any)
- record smoke test result (PASS/FAIL)
- note rollback reason (if rollback occurred)
- link to incident notes/runbook if production impact occurred
