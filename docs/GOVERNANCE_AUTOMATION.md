# Governance — Automation (Review / Merge / Deploy)

**Status:** Active (Policy)
**Last Updated:** 2026-02-20

This document defines what is allowed for **automation** in the FlowBiz ecosystem (agents, CI, and operators), across:

- **Review** (automated checks + advisory review)
- **Merge** (auto-merge after policy gates)
- **Deploy** (auto-deploy to VPS after merge)

It is intended to be used by:
- This repo (`flowbiz-ai-core`)
- Client repos that follow [CLIENT_PROJECT_TEMPLATE.md](CLIENT_PROJECT_TEMPLATE.md)

---

## 1) Definitions

- **Automation**: Any action executed without a human typing commands at the time of execution (e.g., GitHub Actions, auto-merge, scheduled jobs, scripted SSH deploy).
- **Production mutation**: Any operation that changes VPS state (containers, nginx, env files, certificates, firewall).
- **Approved lane**: A deployment/merge path that is auditable, deterministic, and has clear rollback.

---

## 2) Automation Lanes (Approved)

### Lane A — GitHub-native (Preferred)

- **Auto-review**: CI + Guardrails bot + optional Copilot review.
- **Auto-merge**: GitHub Auto-merge enabled on PR after all required checks and required reviews pass.
- **Auto-deploy**: Merge to `main` triggers deploy workflow (example: [.github/workflows/deploy_example.yml](../.github/workflows/deploy_example.yml)).

Why preferred:
- full audit trail (checks, approvals, deployments)
- environment protection rules
- consistent, repeatable and rollbackable

### Lane B — GitHub Actions reusable workflow (Recommended for client repos)

Use the reusable workflow documented in [REUSABLE_DEPLOYMENT.md](REUSABLE_DEPLOYMENT.md).

### Lane C — Local-to-VPS scripted deploy (Allowed, controlled)

Allowed only when:
- the target host is explicit (standard SSH alias: `flowbiz-vps`)
- the remote path is explicit (`/opt/flowbiz/...`)
- the deployment is performed by an **approved script / runbook** (no ad-hoc commands)
- health checks are performed before/after

This lane exists for:
- emergency fixes when CI is unavailable
- VPS diagnostics when workflow runners can’t reach the VPS

**Approved runbook/script:**
- [docs/RUNBOOK_LOCAL_VPS_DEPLOY.md](RUNBOOK_LOCAL_VPS_DEPLOY.md)
- `scripts/vps_deploy.ps1`

---

## 3) Policy Gates (What must be true)

### Auto-review gates

- CI runs (tests + lint)
- Guardrails bot comment is ✅ (advisory, but should be clean)
- For infra changes: CODEOWNERS review is required

Optional:
- Request an automated Copilot review on PRs (advisory). Treat it as a helper, not an approval.

### Auto-merge gates

Auto-merge is allowed only if ALL are true:

- Branch protection requires:
  - CI checks passing (tests + lint)
  - required reviews
  - CODEOWNERS reviews for critical paths
- PR description includes `## Summary` + `## Verification / Testing`
- Exactly one persona label is applied (`persona:core` / `persona:infra` / `persona:docs`)

### Auto-deploy gates

Auto-deploy is allowed only if:

- Deployment is triggered from `main` (or a protected release branch)
- Secrets live in GitHub **Environment** secrets (never in repo)
- Post-deploy health checks run (at least `/healthz`)
- Rollback is documented in the PR (or runbook)

---

## 4) SSH Standard (Local-to-VPS)

### Required SSH host alias

All local runbooks/scripts MUST use this SSH host alias:

```ssh-config
Host flowbiz-vps
  HostName <VPS_IP_OR_DOMAIN>
  User flowbiz
  Port 22
  IdentityFile C:\Users\<You>\.ssh\id_ed25519
  IdentitiesOnly yes
  ServerAliveInterval 60
  ServerAliveCountMax 3
```

Reason:
- avoids “who/where am I deploying to?” ambiguity
- enables safe scripts (`ssh flowbiz-vps ...`) with deterministic targeting

---

## 5) Infra Safety Rules (Still enforced)

These rules remain non-negotiable, even with automation:

- **System nginx only** for production reverse proxy. See [ADR_SYSTEM_NGINX.md](ADR_SYSTEM_NGINX.md).
- **No guessing**: ports/domains/cert paths must be explicit.
- **No secrets in git**.
- **No ad-hoc VPS edits** that are not represented in a PR (except emergency temporary mitigation; must be documented and reverted).

---

## 6) Minimum Rollback Standard

Every automated deploy path must support at least one rollback option:

- Re-deploy previous commit SHA (preferred)
- `docker compose up -d` with previous image tag
- Restore previous nginx vhost config (for routing-only changes)

---

## 7) Related Docs

- [CODEX_AGENT_BEHAVIOR_LOCK.md](CODEX_AGENT_BEHAVIOR_LOCK.md)
- [GUARDRAILS.md](GUARDRAILS.md)
- [REUSABLE_DEPLOYMENT.md](REUSABLE_DEPLOYMENT.md)
- [DEPLOYMENT_VPS.md](DEPLOYMENT_VPS.md)
