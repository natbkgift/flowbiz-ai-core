# Runbook — Local → VPS Deploy (ssh flowbiz-vps)

This runbook uses the standard SSH alias `flowbiz-vps` and a controlled script so deployments are deterministic and auditable.

## Prerequisites

- SSH config contains host alias `flowbiz-vps` (see `docs/GOVERNANCE_AUTOMATION.md`)
- You can `ssh flowbiz-vps` without password prompts (key-based auth)
- The repo already exists on VPS at the target path (default: `/opt/flowbiz/flowbiz-ai-core`)

## Recommended usage (Windows PowerShell)

### 1) Deploy latest `main`

```powershell
powershell -ExecutionPolicy Bypass -File scripts/vps_deploy.ps1 \
  -RemotePath /opt/flowbiz/flowbiz-ai-core \
  -GitRef main \
  -SourceMode upload \
  -ComposeFiles docker-compose.yml docker-compose.override.prod.yml \
  -HealthMode container \
  -HealthUrlLocal http://127.0.0.1:8000/healthz
```

### 2) Deploy a specific commit (rollback)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/vps_deploy.ps1 \
  -RemotePath /opt/flowbiz/flowbiz-ai-core \
  -GitRef <commit-sha> \
  -SourceMode upload \
  -ComposeFiles docker-compose.yml docker-compose.override.prod.yml \
  -HealthMode container \
  -HealthUrlLocal http://127.0.0.1:8000/healthz
```

### 3) Optional: reload system nginx (only if you know you changed vhosts)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/vps_deploy.ps1 \
  -RemotePath /opt/flowbiz/flowbiz-ai-core \
  -GitRef main \
  -ReloadNginx \
  -HealthUrlLocal http://127.0.0.1:8000/healthz
```

## Safety notes

- The script refuses `RemotePath` outside `/opt/flowbiz/`.
- `-ReloadNginx` runs `sudo nginx -t` before `sudo systemctl reload nginx`.
- This is intended for the approved automation lane described in `docs/GOVERNANCE_AUTOMATION.md`.
