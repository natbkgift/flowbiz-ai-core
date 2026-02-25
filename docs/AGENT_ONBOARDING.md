# Agent Onboarding — FlowBiz VPS

For contributor/agent onboarding within this core repo (non-deploy workflow), also read `docs/ONBOARDING_FLOW.md` (PR-110).

**Purpose:** This document provides actionable instructions for new agents/teams deploying additional services to the FlowBiz VPS without breaking existing infrastructure.

---

## 📖 Read This First

Before deploying any service, review these essential documents:

1. **[CODEX_AGENT_BEHAVIOR_LOCK.md](CODEX_AGENT_BEHAVIOR_LOCK.md)** — Mandatory agent behavior rules and safety locks
2. **[VPS_STATUS.md](VPS_STATUS.md)** — Current production state, deployed services, and operational conventions
3. **[CLIENT_PROJECT_TEMPLATE.md](CLIENT_PROJECT_TEMPLATE.md)** — Template and requirements for new service projects
4. **[DEPLOYMENT_VPS.md](DEPLOYMENT_VPS.md)** — Detailed deployment procedures and troubleshooting

**Rule:** If you haven't read the above documents, do not proceed with deployment.

---

## ✅ Allowed Actions

You **MAY** do the following:

### Deployment & Services
- ✅ Deploy new services under `/opt/flowbiz/clients/<service-name>/`
- ✅ Create your own docker-compose files for your service
- ✅ Use unique internal ports for your containers (avoid 8000, 5432, 80, 443)
- ✅ Create separate nginx configurations or use subdomains
- ✅ Add your own SSL certificates for subdomains (via certbot)
- ✅ Create isolated Docker networks for your service
- ✅ Use separate environment files (`.env`) with service-specific credentials

### Monitoring & Debugging
- ✅ Read logs from your own containers (`docker compose logs -f`)
- ✅ Check the status of your containers (`docker compose ps`)
- ✅ Test your endpoints with `curl` or similar tools
- ✅ View system resources (`docker stats`, `df -h`, `free -m`)
- ✅ Check certbot timers (`systemctl list-timers`)

### Documentation
- ✅ Update your service's README and deployment docs
- ✅ Document your service's integration points
- ✅ Propose documentation improvements via PR

---

## ❌ Forbidden Actions

You **MUST NOT** do the following:

### Infrastructure Changes
- ❌ Edit global nginx configs (anything outside your service vhost file in `/etc/nginx/conf.d/`)
- ❌ Stop, restart, or modify `flowbiz-ai-core` containers (api, postgres)
- ❌ Remove or modify the `postgres-data` volume
- ❌ Change firewall rules without authorization (`ufw`, iptables)
- ❌ Modify systemd services (certbot timer, docker daemon)

### Port & Network
- ❌ Bind services to `0.0.0.0:80` or `0.0.0.0:443` (system nginx owns 80/443)
- ❌ Bind to ports already used by core services (8000, 5432)
- ❌ Expose database ports publicly (5432, 3306, etc.)
- ❌ Bypass the reverse proxy for public endpoints

### Code & Configuration
- ❌ Push code to `natbkgift/flowbiz-ai-core` repository (create your own repo)
- ❌ Merge UI, billing, or platform logic into core API
- ❌ Commit secrets, API keys, or `.env` files to version control
- ❌ Modify shared libraries without coordination

### Destructive Operations
- ❌ Run `docker compose down -v` on core services (deletes data)
- ❌ Delete or truncate core database tables
- ❌ Remove SSL certificates at `/etc/letsencrypt/live/flowbiz.cloud/`

---

## 🎯 Required Endpoints for Any New Service

All services deployed on the VPS **MUST** implement these endpoints:

### 1. Health Check
```http
GET /healthz
```

**Response:**
```json
{
  "status": "ok",
  "service": "your-service-name",
  "version": "x.y.z"
}
```

**Status Code:** `200 OK`

**Purpose:** Load balancer health checks, uptime monitoring

### 2. Metadata
```http
GET /v1/meta
```

**Response:**
```json
{
  "service": "your-service-name",
  "environment": "production",
  "version": "x.y.z",
  "build_sha": "abc123"
}
```

**Status Code:** `200 OK`

**Purpose:** Runtime metadata for observability and debugging

### Why These Endpoints Matter
- Health checks enable automated monitoring and alerting
- Metadata endpoints help with version tracking and incident response
- Standardization makes operations predictable across all services

---

## 🚀 Standard Run Modes

Every service should support these run modes:

### 1. Local Development
```bash
# Virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .[dev]

# Run service (adjust module path for your service structure)
uvicorn apps.api.main:app --reload --port <YOUR_PORT>
```

**Environment:** Use `.env` with `APP_ENV=dev`

### 2. Docker Compose (Development)
```bash
# Copy environment file
cp .env.example .env

# Edit with dev values
nano .env

# Start stack
docker compose up --build
```

**Environment:** Use `.env` with `APP_ENV=dev`

### 3. Docker Compose (Production Override)
```bash
# On VPS
cd /opt/flowbiz/clients/<your-service>

# Use production override
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Environment:** Use `.env.prod` with `APP_ENV=production`

---

## 📁 Directory Convention on VPS

### Standard Layout
```
/opt/flowbiz/
├── flowbiz-ai-core/              # Core API (Phase 1) — DO NOT MODIFY
│   ├── docker-compose.yml
│   ├── .env
│   ├── nginx/
│   └── ...
├── clients/
│   ├── service-alpha/            # Your service here
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.prod.yml
│   │   ├── .env.prod
│   │   ├── nginx/
│   │   └── ...
│   ├── service-beta/             # Another service
│   │   └── ...
│   └── service-gamma/            # Yet another service
│       └── ...
└── shared/                       # Optional shared resources
    └── ...
```

### Deployment Path Rules
1. **Core API:** `/opt/flowbiz/flowbiz-ai-core` (read-only for agents)
2. **Your Service:** `/opt/flowbiz/clients/<service-name>` (your working directory)
3. **Naming:** Use lowercase, hyphens (kebab-case), descriptive names

### Example: Deploying "customer-support-api"
```bash
# Navigate to clients directory
cd /opt/flowbiz/clients

# Clone your repository
git clone https://github.com/your-org/customer-support-api.git

# Navigate to service directory
cd customer-support-api

# Set up environment
cp .env.example .env.prod
nano .env.prod

# Deploy
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify
curl http://localhost:<YOUR_PORT>/healthz
```

---

## 🧪 Minimal Smoke Test Commands

After deploying your service, run these tests to verify basic functionality:

### 1. Check Container Status
```bash
docker compose ps
```

**Expected:** All your containers show `Up` or `Up (healthy)` status.

### 2. Test Health Endpoint (Internal)
```bash
curl http://localhost:<YOUR_PORT>/healthz
```

**Expected:** `200 OK` with `{"status":"ok",...}`

### 3. Test Metadata Endpoint (Internal)
```bash
curl http://localhost:<YOUR_PORT>/v1/meta
```

**Expected:** `200 OK` with version information

### 4. Test via Nginx (If Configured)
```bash
# Path-based routing
curl https://flowbiz.cloud/<your-service-path>/healthz

# OR subdomain routing
curl https://<your-service>.flowbiz.cloud/healthz
```

**Expected:** `200 OK` through reverse proxy

### 5. Verify Security Headers
```bash
curl -I https://<your-service>.flowbiz.cloud/healthz
```

**Expected Headers:**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Strict-Transport-Security: max-age=...`

### 6. Check Logs for Errors
```bash
docker compose logs --tail=50
```

**Expected:** No critical errors (500s, crashes, connection failures)

---

## 🔄 Rollback Protocol

If your deployment causes issues or breaks functionality, follow these steps to rollback:

### When to Rollback

Rollback immediately if you observe:
- ❌ Health checks failing after deployment
- ❌ Critical errors in container logs
- ❌ Service unavailable or returning 500 errors
- ❌ Database connection failures
- ❌ Breaking changes affecting other services

### Rollback Steps

#### Option 1: Revert to Previous Git Tag (Recommended)
```bash
# For client services:
cd /opt/flowbiz/clients/<your-service>

# For core service (authorized personnel only):
# cd /opt/flowbiz/flowbiz-ai-core

# Check current version
git describe --tags

# Rollback to last stable version
git checkout tags/vX.X.X  # Replace with your last stable tag (e.g., v1.0.0)

# Restart containers with pinned version
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

# Verify
curl http://localhost:<YOUR_PORT>/healthz
```

#### Option 2: Revert Last Commit
```bash
# Navigate to your service directory
cd /opt/flowbiz/clients/<your-service>

# Revert to previous commit
git log --oneline -5  # Find the last good commit SHA (check messages/timestamps)
git checkout <commit-sha>  # Replace with actual SHA of last known good commit

# Restart containers
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify
curl http://localhost:<YOUR_PORT>/healthz
```

#### Option 3: Revert PR in GitHub (For Main Branch)
1. **Create a revert PR** on GitHub:
   - Go to the problematic PR
   - Click "Revert" button
   - GitHub will create a new PR that reverts the changes
   
2. **Merge the revert PR** immediately

3. **Pull and redeploy** on VPS:
   ```bash
   # Navigate to your service directory
   cd /opt/flowbiz/clients/<your-service>
   
   git pull origin main
   docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

### Post-Rollback Checklist

After rolling back, verify:
- [ ] Health endpoint returns `200 OK`
- [ ] Metadata endpoint shows correct (old) version
- [ ] No errors in container logs (`docker compose logs --tail=50`)
- [ ] Dependent services still working (if any)
- [ ] Document the incident and rollback reason

### Communication

After rollback, you **MUST**:
1. **Document the issue** — What broke and why
2. **Notify via PR comment** — Add a comment on the problematic PR explaining the rollback
3. **Update PR Log** — Add entry to `docs/PR_LOG.md` (if applicable)
4. **Create post-mortem** — For critical issues, create an incident report

### Prevention

To make rollbacks easier:
- ✅ Always tag stable releases (`git tag v1.0.0`)
- ✅ Use version pinning in `docker-compose.prod.yml`
- ✅ Keep database migrations reversible
- ✅ Test in staging/local before production
- ✅ Deploy during low-traffic periods
- ✅ Monitor logs immediately after deployment

---

## 🔐 Security Checklist

Before going live, ensure:

- [ ] `.env` file has restrictive permissions (`chmod 600 .env.prod`)
- [ ] No secrets committed to Git (use `.gitignore` for `.env`, `.env.prod`)
- [ ] Database passwords are strong and unique
- [ ] API keys are stored in environment variables, not hardcoded
- [ ] CORS origins configured correctly (no `*` in production)
- [ ] SSL certificate provisioned and auto-renewal working
- [ ] Security headers present in all responses
- [ ] No public exposure of internal ports (database, cache, etc.)
- [ ] Rate limiting enabled (if applicable)
- [ ] Input validation implemented for all endpoints

---

## 🆘 Escalation Rules

### When to Ask for Help

If you encounter any of the following, **STOP** and escalate:

1. **Uncertainty about infrastructure changes**  
   → Do not proceed; propose a doc-only PR or ask for review

2. **Core services appear broken** (system nginx routing, api, postgres)  
   → Do not attempt fixes; notify the core team immediately

3. **SSL certificate issues** affecting `flowbiz.cloud`  
   → Do not touch certbot for the core domain; escalate

4. **Port conflicts** with core services  
   → Do not force-bind ports; find alternative ports or escalate

5. **Database schema conflicts** or shared resource contention  
   → Do not apply migrations to core DB; coordinate with core team

### How to Escalate

1. **Document the issue** — Collect error messages, logs, symptoms
2. **Propose doc-only PR** — If it's a documentation gap or unclear requirement
3. **Create GitHub issue** — For bugs, feature requests, or infrastructure questions
4. **Contact core team** — For urgent production issues or downtime

### Safe Fallback
When in doubt:
- ✅ **DO:** Create a doc-only PR proposing your approach
- ✅ **DO:** Ask questions via GitHub issues
- ✅ **DO:** Test changes in local Docker first
- ❌ **DO NOT:** Make destructive changes to production
- ❌ **DO NOT:** Assume your change won't affect core services

---

## 📚 Quick Reference

### Essential Commands
```bash
# Check core services status (read-only)
cd /opt/flowbiz/flowbiz-ai-core && docker compose ps

# Check your service status
cd /opt/flowbiz/clients/<your-service> && docker compose ps

# View your service logs
docker compose logs -f

# Restart your service only
docker compose restart

# Update your service
git pull origin main
docker compose up --build -d

# Test core API health (should always work)
curl https://flowbiz.cloud/healthz
```

### Port Allocation Guide
| Port Range | Usage |
|------------|-------|
| 80, 443 | Reserved for nginx (core) |
| 8000 | Reserved for core API |
| 5432 | Reserved for core database |
| 8001-8099 | Available for client services (internal) |
| 5433-5499 | Available for client databases (internal) |
| 6379-6399 | Available for Redis/cache (internal) |

**Note:** All ports are internal. Use nginx reverse proxy for external access.

### Environment Variable Prefixes
- `APP_*` — Application settings (strict, validated by Pydantic)
- `FLOWBIZ_*` — Metadata and version info (read by core/deployment)
- `POSTGRES_*` — Database configuration
- `<SERVICE>_*` — Service-specific settings (use your service name as prefix)

---

## 🎓 Learning Resources

### FlowBiz-Specific Docs
- [VPS Status](VPS_STATUS.md) — Current production state
- [Client Project Template](CLIENT_PROJECT_TEMPLATE.md) — Service template and contract
- [Deployment Guide](DEPLOYMENT_VPS.md) — Detailed deployment steps
- [Architecture](ARCHITECTURE.md) — System design and patterns
- [PR Log](PR_LOG.md) — Change history

### External Resources
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## ✅ Pre-Deployment Checklist

Before deploying a new service, verify:

- [ ] Service follows `CLIENT_PROJECT_TEMPLATE.md` structure
- [ ] `/healthz` and `/v1/meta` endpoints implemented
- [ ] `docker-compose.yml` and `docker-compose.prod.yml` ready
- [ ] `.env.example` documented with all required variables
- [ ] `.env.prod` created with production values (not committed)
- [ ] Unique ports assigned (no conflicts with core)
- [ ] Nginx configuration prepared (if using reverse proxy)
- [ ] SSL certificate provisioned (if using subdomain)
- [ ] Local smoke tests passed (`docker compose up` + curl tests)
- [ ] Documentation updated (README, deployment guide)
- [ ] Security checklist reviewed and completed

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-24  
**Maintained by:** FlowBiz Core Team

**Remember:** When in doubt, ask first. It's better to overcommunicate than to break production.
