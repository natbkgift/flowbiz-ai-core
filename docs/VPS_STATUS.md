# VPS Status — FlowBiz Core Phase 1

**Last Updated:** 2025-12-26

---

## VPS Overview

### Purpose
This VPS hosts the production deployment of **FlowBiz AI Core** (Phase 1), serving as the foundational API service layer for the FlowBiz ecosystem at `flowbiz.cloud`.

### Environment
- **Operating System:** Ubuntu 24.04 LTS
- **Hosting Provider:** Hostinger VPS
- **Domain:** `flowbiz.cloud` + `www.flowbiz.cloud`
- **SSL/TLS:** Let's Encrypt certificates with auto-renewal
- **Reverse Proxy:** Nginx (running in Docker container)

### Network Configuration
- **HTTP (Port 80):** Redirects all traffic to HTTPS
- **HTTPS (Port 443):** Serves all public endpoints with valid SSL certificate
- **Internal Ports:** Service containers communicate internally (not exposed publicly)

---

## Current Deployed Services (Phase 1)

### FlowBiz AI Core v0.1.0

**Repository:** `natbkgift/flowbiz-ai-core`  
**Deployment Path:** `/opt/flowbiz/flowbiz-ai-core`  
**Version:** `0.1.0`

#### Container Stack
The following Docker containers are running via Docker Compose:

1. **nginx** — Nginx reverse proxy (1.25-alpine)
   - Handles SSL termination
   - Routes requests to API service
   - Applies security headers
   - Manages HTTP → HTTPS redirect

2. **api** — FastAPI application (flowbiz-ai-core:dev)
   - Python-based REST API
   - Internal port: 8000 (not exposed)
   - Provides health checks, metadata, and business endpoints

3. **postgres** — PostgreSQL database (16-alpine)
   - Data persistence layer
   - Internal port: 5432 (not exposed)
   - Volume: `postgres-data`

#### Port Mapping
- **Public:** 80 (HTTP redirect), 443 (HTTPS)
- **Internal:** 8000 (API), 5432 (Database)
- **Exposed:** Only ports 80 and 443 are accessible from the internet

---

## Verified Production Checks

### 1. Health Endpoint
```bash
curl https://flowbiz.cloud/healthz
```

**Expected Response:**
```json
{"status":"ok","service":"FlowBiz AI Core","version":"0.1.0"}
```

**Status:** ✅ Working

### 2. Metadata Endpoint
```bash
curl https://flowbiz.cloud/v1/meta
```

**Expected Response:**
```json
{"service":"FlowBiz AI Core","version":"0.1.0","git_sha":"[commit-sha]","environment":"production"}
```

**Status:** ✅ Working

### 3. HTTP → HTTPS Redirect
```bash
curl -I http://flowbiz.cloud/healthz
```

**Expected:** `301 Moved Permanently` redirect to `https://flowbiz.cloud/healthz`

**Status:** ✅ Working

### 4. Security Headers Verification
```bash
curl -I https://flowbiz.cloud/healthz
```

**Expected Headers:**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`

**Status:** ✅ All headers present

### 5. API Documentation
```bash
curl https://flowbiz.cloud/docs
```

**Expected:** OpenAPI/Swagger UI (HTML response)

**Status:** ✅ Working

---

## TLS/SSL Details

### Certificate Location
```
/etc/letsencrypt/live/flowbiz.cloud/fullchain.pem
/etc/letsencrypt/live/flowbiz.cloud/privkey.pem
```

### Certificate Authority
Let's Encrypt

### Renewal Strategy
- **Method:** Certbot with systemd timer
- **Frequency:** Automatic renewal attempts twice daily
- **Timer Status Check:**
  ```bash
  sudo systemctl status certbot.timer
  ```

- **Manual Dry-Run Test:**
  ```bash
  sudo certbot renew --dry-run
  ```

### SSL Configuration
- **Protocols:** TLSv1.2, TLSv1.3
- **Ciphers:** HIGH:!aNULL:!MD5
- **HSTS:** max-age=63072000 (2 years) with includeSubDomains and preload

---

## Operational Conventions (Adding More Projects)

### Folder Layout
All FlowBiz projects should be deployed under `/opt/flowbiz/` with the following structure:

```
/opt/flowbiz/
├── flowbiz-ai-core/          # Current Phase 1 deployment
├── clients/
│   ├── service-name-1/       # Future client service
│   ├── service-name-2/       # Future client service
│   └── service-name-3/       # Future client service
└── shared/                   # Shared resources (if needed)
```

### Per-Project Requirements
Each project must maintain:
1. **Own docker-compose file(s)** — No sharing of compose files between projects
2. **Unique port assignments** — No host port conflicts (use different internal ports)
3. **Nginx vhost configuration** — Each service should have its own reverse proxy configuration or subdomain
4. **Environment isolation** — Separate `.env` files with service-specific credentials
5. **Health check endpoint** — Minimum: `GET /healthz` returning 200 OK

### Nginx Routing Strategies
Choose one approach per new service:

**Option 1: Path-based routing**
```
https://flowbiz.cloud/service-name/...
```

**Option 2: Subdomain routing (recommended)**
```
https://service-name.flowbiz.cloud/...
```

**Option 3: Separate domain**
```
https://service-name.com/...
```

---

## Hard Rules (MUST NOT)

### Do Not Edit Global Nginx
❌ **DO NOT** modify the core nginx configuration (`/opt/flowbiz/flowbiz-ai-core/nginx/`) unless explicitly authorized by the core team.

**Reason:** Breaking nginx breaks all services including the core API.

**Alternative:** Create a separate nginx container or vhost for your service.

### Do Not Expose Random Ports Publicly
❌ **DO NOT** bind services directly to public ports (e.g., `0.0.0.0:8080`) without reverse proxy and security review.

**Reason:** Security risk, no SSL termination, no security headers, no rate limiting.

**Alternative:** Always use nginx or another reverse proxy with proper SSL and security headers.

### Do Not Break Existing Stack
❌ **DO NOT** stop, remove, or modify containers/volumes belonging to `flowbiz-ai-core` (nginx, api, db, postgres-data volume).

**Reason:** Downtime affects production users.

**Alternative:** Deploy your service as an independent stack with isolated resources.

### Do Not Deploy UI/Billing/Platform Logic Inside Core
❌ **DO NOT** add frontend code, billing endpoints, or platform management logic to the `flowbiz-ai-core` repository.

**Reason:** Core is designed as a foundational API layer only. Other concerns belong in separate repositories.

**Alternative:** Create a new client project following the `CLIENT_PROJECT_TEMPLATE.md`.

### Do Not Store Secrets in Version Control
❌ **DO NOT** commit `.env` files, API keys, passwords, or certificates to Git.

**Reason:** Security vulnerability, credential leakage.

**Alternative:** Use `.env.example` as a template and manage secrets via environment variables or secure secret management tools.

---

## Troubleshooting Quick Notes

### Check Running Containers
```bash
cd /opt/flowbiz/flowbiz-ai-core
docker compose ps
```

**Expected:** All three services (nginx, api, db) should show `Up` or `Up (healthy)` status.

### View Container Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f nginx
docker compose logs -f db

# Last 100 lines
docker compose logs --tail=100 api
```

### Common Symptoms & Checks

#### Symptom: "502 Bad Gateway"
**Possible Causes:**
- API container not running
- API container crashed
- Database connection failure

**Check:**
```bash
docker compose ps api
docker compose logs api
```

#### Symptom: "SSL certificate not found"
**Possible Causes:**
- Certificate expired or not renewed
- Certificate path incorrect

**Check:**
```bash
sudo systemctl status certbot.timer
sudo certbot certificates
ls -la /etc/letsencrypt/live/flowbiz.cloud/
```

#### Symptom: "Connection refused"
**Possible Causes:**
- Firewall blocking ports
- Docker not running
- Nginx not running

**Check:**
```bash
sudo ufw status
sudo systemctl status docker
docker compose ps nginx
```

#### Symptom: Database connection errors in API logs
**Possible Causes:**
- Database container not healthy
- Wrong credentials in `.env`
- Database volume corrupted

**Check:**
```bash
docker compose ps db
docker compose logs db
docker compose exec db psql -U flowbiz -d flowbiz -c "SELECT 1;"
```

### Safe Read-Only Commands
These commands are safe to run and won't disrupt services:

```bash
# List all containers
docker ps -a

# View compose configuration
docker compose config

# Check container resource usage
docker stats

# List systemd timers (certbot)
systemctl list-timers

# Check open ports
sudo netstat -tlnp | grep -E ':(80|443|8000|5432)'

# Test internal API directly
docker compose exec api curl http://localhost:8000/healthz
```

### Rollback Procedures

If a deployment causes issues, use these steps to rollback to a previous stable version:

#### Rollback to Tagged Version
```bash
cd /opt/flowbiz/flowbiz-ai-core

# Check current version
git describe --tags

# List available tags
git tag -l

# Rollback to specific version
git checkout tags/vX.X.X  # Replace with your desired version tag (e.g., v0.1.0)

# Rebuild and restart containers
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

# Verify services are running
docker compose ps
curl https://flowbiz.cloud/healthz
```

#### Quick Rollback (Last Known Good)
```bash
cd /opt/flowbiz/flowbiz-ai-core

# Revert to last commit on main branch
git checkout main
git pull origin main

# Restart with last stable version
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify
curl https://flowbiz.cloud/healthz
```

**Important Notes:**
- Always verify health checks after rollback
- Database migrations may need manual intervention if schema changed
- Check logs after rollback: `docker compose logs -f`
- Document the rollback in PR_LOG.md or create an incident report

---

## Contact / Ownership

**Maintained by:** FlowBiz Core Team

For questions, issues, or infrastructure changes:
1. Review existing documentation: `docs/DEPLOYMENT_VPS.md`, `docs/ARCHITECTURE.md`, `docs/CLIENT_PROJECT_TEMPLATE.md`
2. Check troubleshooting section above
3. If uncertain about infrastructure changes, propose a doc-only PR first for review
4. Do not make destructive changes without approval

---

## Related Documentation

- **[Deployment Guide](DEPLOYMENT_VPS.md)** — Step-by-step VPS deployment instructions
- **[Agent Onboarding](AGENT_ONBOARDING.md)** — Quick start for new agents deploying services
- **[Client Project Template](CLIENT_PROJECT_TEMPLATE.md)** — Template for new service projects
- **[Architecture](ARCHITECTURE.md)** — System design and technical architecture
- **[PR Log](PR_LOG.md)** — Historical record of all changes

---

**Document Version:** 1.0  
**VPS Phase:** Phase 1 (Core API only)  
**Next Steps:** Phase 2 will add client services following the conventions outlined above.
