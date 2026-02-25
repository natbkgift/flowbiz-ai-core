# Runbook — Local → VPS Deploy (ssh flowbiz-vps)

This runbook uses the standard SSH alias `flowbiz-vps` and a controlled script so deployments are deterministic and auditable.

For release promotion and rollback (tag/app version/promotion flow), see:
- [docs/RELEASE_ROLLBACK_RUNBOOK.md](RELEASE_ROLLBACK_RUNBOOK.md)

## Prerequisites

- SSH config contains host alias `flowbiz-vps` (see `docs/GOVERNANCE_AUTOMATION.md`)
- You can `ssh flowbiz-vps` without password prompts (key-based auth)
- The repo already exists on VPS at the target path (default: `/opt/flowbiz/flowbiz-ai-core`)

## Recommended usage (Windows PowerShell)

### 1) Deploy latest `main` (normal path: `SourceMode=git`)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/vps_deploy.ps1 `
  -RemotePath /opt/flowbiz/flowbiz-ai-core `
  -GitRef main `
  -SourceMode git `
  -ComposeFiles docker-compose.yml docker-compose.prod-api.yml `
  -HealthMode host `
  -HealthUrlLocal http://127.0.0.1:8000/healthz `
  -PublicHealthUrl https://flowbiz.cloud/api/healthz
```

### 2) Deploy a specific commit (rollback or candidate deploy)

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

### 3) Local unpushed changes (advanced): `SourceMode=upload`

Use only when you intentionally need to deploy a local commit that is not on `origin` yet.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/vps_deploy.ps1 `
  -RemotePath /opt/flowbiz/flowbiz-ai-core `
  -GitRef <local-commit-sha> `
  -SourceMode upload `
  -ComposeFiles docker-compose.yml docker-compose.prod-api.yml `
  -HealthMode host `
  -HealthUrlLocal http://127.0.0.1:8000/healthz `
  -PublicHealthUrl https://flowbiz.cloud/api/healthz
```

### 4) Optional: clean dirty remote git working tree before `SourceMode=git`

If the VPS repo was previously modified by `SourceMode=upload` or manual edits and `git` deploy fails with "working tree not clean", rerun with:

```powershell
-ResetRemoteGitWorkingTree
```

This is **explicit** on purpose (the script fails by default rather than cleaning remote files silently).

### 5) Optional: reload system nginx (only if you know you changed vhosts)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/vps_deploy.ps1 `
  -RemotePath /opt/flowbiz/flowbiz-ai-core `
  -GitRef main `
  -ReloadNginx `
  -HealthUrlLocal http://127.0.0.1:8000/healthz
```

## Safety notes

- The script refuses `RemotePath` outside `/opt/flowbiz/`.
- `-ReloadNginx` runs `sudo nginx -t` before `sudo systemctl reload nginx`.
- `SourceMode=git` now fails fast if the remote repo is dirty (unless `-ResetRemoteGitWorkingTree` is passed).
- Native command failures (`ssh`, `scp`, `git`) are treated as hard failures (no silent success on disconnect).
- This is intended for the approved automation lane described in `docs/GOVERNANCE_AUTOMATION.md`.
