# Incident Runbook — PR-060

> **Scope:** docs-only — operational guidance for FlowBiz AI Core incidents.

## Severity Levels

| Level | Description | Response Time | Escalation |
|-------|-------------|---------------|------------|
| SEV-1 | Service down / data loss | 15 min | Immediate |
| SEV-2 | Major feature broken | 30 min | Within 1 hour |
| SEV-3 | Minor degradation | 2 hours | Within 4 hours |
| SEV-4 | Cosmetic / low impact | Next business day | N/A |

## Common Scenarios

### 1. API not responding (SEV-1)

```bash
# 1. Check container status
ssh flowbiz-vps "docker compose -f docker-compose.yml -f docker-compose.prod-api.yml ps"

# 2. Check logs
ssh flowbiz-vps "docker compose -f docker-compose.yml -f docker-compose.prod-api.yml logs --tail=100 api"

# 3. Restart
ssh flowbiz-vps "docker compose -f docker-compose.yml -f docker-compose.prod-api.yml restart api"

# 4. Verify
curl -s https://flowbiz.cloud/api/healthz
```

### 2. High error rate (SEV-2)

```bash
# Check recent errors in logs
ssh flowbiz-vps "docker compose -f docker-compose.yml -f docker-compose.prod-api.yml logs --since=10m api | grep ERROR"

# Check error aggregation (when endpoint is deployed)
curl -s https://flowbiz.cloud/api/v1/agent/health
```

### 3. Slow responses (SEV-3)

- Check `SlowQuerySnapshot` for operations exceeding threshold
- Check `RequestAnalyticsSnapshot.p95_duration_ms`
- Review recent deploys for regressions
- Check VPS resource utilization: `ssh flowbiz-vps "top -b -n1 | head -20"`

### 4. Deploy failure (SEV-3)

```bash
# Check git status on VPS
ssh flowbiz-vps "cd /opt/flowbiz/flowbiz-ai-core && git status"

# Force sync to origin/main
ssh flowbiz-vps "cd /opt/flowbiz/flowbiz-ai-core && git fetch origin main && git reset --hard origin/main"

# Rebuild
ssh flowbiz-vps "cd /opt/flowbiz/flowbiz-ai-core && docker compose -f docker-compose.yml -f docker-compose.prod-api.yml up -d --build"
```

## Post-Incident

1. Write a brief incident report (what happened, timeline, root cause)
2. Update alert rules if the issue was not caught
3. Add regression test if applicable
4. Update this runbook with new scenarios

## Contacts

| Role | Contact |
|------|---------|
| On-call engineer | (defined per team) |
| Platform lead | (defined per team) |
