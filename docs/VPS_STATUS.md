# VPS Status — FlowBiz Multi-Project VPS

**Last Updated:** 2025-12-26

---

## VPS Overview

### Purpose
This VPS hosts production deployments for **FlowBiz AI Core** and multiple client projects, serving as the foundational infrastructure for the FlowBiz ecosystem at `flowbiz.cloud`.

### Environment
- **Operating System:** Ubuntu 24.04 LTS
- **Hosting Provider:** Hostinger VPS
- **Domain:** `flowbiz.cloud` + `www.flowbiz.cloud`
- **SSL/TLS:** Let's Encrypt certificates with auto-renewal (via Certbot)
- **Reverse Proxy:** System Nginx (via systemd) — **MANDATORY** for all projects

### Network Configuration
- **HTTP (Port 80):** Redirects all traffic to HTTPS (managed by system nginx)
- **HTTPS (Port 443):** Serves all public endpoints with valid SSL certificate (managed by system nginx)
- **Internal Ports:** Service containers bind to localhost only (e.g., 127.0.0.1:3001, 127.0.0.1:8000)
- **Routing:** System nginx proxies requests to localhost ports based on domain/path rules

---

## Infrastructure Architecture (MANDATORY)

### System Nginx — The Only Reverse Proxy

**CRITICAL:** System nginx via systemd is the **ONLY** allowed reverse proxy. Docker-based nginx, Traefik, Caddy, or any containerized proxy solutions are **FORBIDDEN** in production.

**Why System Nginx:**
- Owns ports 80/443 once for all projects
- Provides stable TLS certificate management with Let's Encrypt
- Enables centralized routing in `/etc/nginx/conf.d/`
- Prevents port conflicts between multiple projects
- See [ADR_SYSTEM_NGINX.md](ADR_SYSTEM_NGINX.md) for full rationale

**Verification:**
```bash
# No nginx containers should exist in production
docker ps --filter "name=nginx" --filter "ancestor=nginx"
# Expected: No results

# System nginx must own ports 80/443
sudo systemctl status nginx
sudo netstat -tlnp | grep ':80\|:443'
# Expected: nginx process via systemd
```

---

## Current Deployed Services

### FlowBiz AI Core

**Repository:** `natbkgift/flowbiz-ai-core`  
**Deployment Path:** `/opt/flowbiz/flowbiz-ai-core`  
**Version:** `0.1.0+`

#### Container Stack
The following Docker containers run via Docker Compose (services only, no nginx):

1. **api** — FastAPI application (flowbiz-ai-core)
   - Python-based REST API
   - Binds to: `127.0.0.1:8000` (localhost only)
   - Provides health checks, metadata, and business endpoints

2. **postgres** — PostgreSQL database (16-alpine)
   - Data persistence layer
   - Binds to: `127.0.0.1:5432` (localhost only)
   - Volume: `postgres-data`

#### Nginx Configuration
- **Location:** `/etc/nginx/conf.d/flowbiz.cloud.conf`
- **Upstream:** `proxy_pass http://127.0.0.1:8000;`
- **Domain:** `flowbiz.cloud` and `www.flowbiz.cloud`
- **SSL Certificates:** `/etc/letsencrypt/live/flowbiz.cloud/`

#### Port Mapping
- **Public (System Nginx):** 80 (HTTP redirect), 443 (HTTPS)
- **Internal (Docker):** 127.0.0.1:8000 (API), 127.0.0.1:5432 (Database)
- **Routing:** System nginx proxies public traffic to localhost ports

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

**Status:** ✅ Working (handled by system nginx)

### 4. Security Headers Verification
```bash
curl -I https://flowbiz.cloud/healthz
```

**Expected Headers (from system nginx):**
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

### 6. System Nginx Verification
```bash
# Check nginx service status
sudo systemctl status nginx

# Check nginx is listening on ports 80/443
sudo netstat -tlnp | grep nginx

# Verify nginx config syntax
sudo nginx -t
```

**Expected:** 
- Nginx service active and running
- Ports 80 and 443 bound to nginx
- Config syntax OK

**Status:** ✅ System nginx operational

---

## TLS/SSL Details (System Nginx)

### Certificate Location
System nginx certificates managed by Certbot:
```
/etc/letsencrypt/live/flowbiz.cloud/fullchain.pem
/etc/letsencrypt/live/flowbiz.cloud/privkey.pem
```

### Certificate Authority
Let's Encrypt

### Renewal Strategy
- **Method:** Certbot with systemd timer (on host system, not in containers)
- **Frequency:** Automatic renewal attempts twice daily
- **Timer Status Check:**
  ```bash
  sudo systemctl status certbot.timer
  ```

- **Manual Dry-Run Test:**
  ```bash
  sudo certbot renew --dry-run
  ```

### SSL Configuration (in system nginx)
- **Protocols:** TLSv1.2, TLSv1.3
- **Ciphers:** HIGH:!aNULL:!MD5
- **HSTS:** max-age=63072000 (2 years) with includeSubDomains and preload

### Why System Nginx for Certificates?
- Certificates persist on host filesystem, not in ephemeral containers
- Certbot integrates directly with systemd for automated renewal
- Certificate reload via `sudo systemctl reload nginx` (stable and predictable)
- No volume mount complexity or container rebuilds required

---

## Operational Conventions (Multi-Project VPS)

### ABSOLUTE RULES (NON-NEGOTIABLE)

These rules are **mandatory** for all projects on this VPS. Violation will result in deployment rejection and rollback.

1. **System nginx via systemd is the ONLY allowed reverse proxy**
   - Docker-based nginx / ingress / traefik / caddy are **FORBIDDEN**
   - All routing configs MUST live under `/etc/nginx/conf.d/`
   - One domain = one nginx config file

2. **Client services MUST bind to localhost ports**
   - Use `127.0.0.1:<PORT>` in docker-compose port mappings
   - Example: `ports: ["127.0.0.1:3001:3001"]`
   - **NEVER** bind to `0.0.0.0:80` or `0.0.0.0:443`

3. **This repo MUST NOT contain client-specific logic**
   - No client app code, no billing logic, no UI code
   - Client projects belong in separate repositories
   - See [CLIENT_PROJECT_TEMPLATE.md](CLIENT_PROJECT_TEMPLATE.md)

4. **No changes to VPS runtime state from this repo**
   - No direct VPS modifications via code
   - No automated nginx reloads from CI
   - Infrastructure changes require manual review and execution

### Folder Layout
All FlowBiz projects should be deployed under `/opt/flowbiz/` with the following structure:

```
/opt/flowbiz/
├── flowbiz-ai-core/          # Core API (localhost:8000)
├── clients/
│   ├── service-alpha/        # Client service (localhost:3001)
│   ├── service-beta/         # Client service (localhost:3002)
│   └── service-gamma/        # Client service (localhost:3003)
└── shared/                   # Shared resources (if needed)
```

### System Nginx Configuration Layout
All nginx configs MUST be in `/etc/nginx/conf.d/`:

```
/etc/nginx/conf.d/
├── flowbiz.cloud.conf              # Core API domain
├── service-alpha.flowbiz.cloud.conf   # Client service subdomain
├── service-beta.flowbiz.cloud.conf    # Client service subdomain
└── service-gamma.example.com.conf     # Client service custom domain
```

**One domain = one config file = one upstream target = clear routing**

### Per-Project Requirements
Each project must maintain:
1. **Own docker-compose file(s)** — No sharing of compose files between projects
2. **Unique localhost port** — No port conflicts (document port allocation)
3. **Nginx config in `/etc/nginx/conf.d/`** — Using the [client_system_nginx.conf.template](../nginx/templates/client_system_nginx.conf.template)
4. **Environment isolation** — Separate `.env` files with service-specific credentials
5. **Health check endpoint** — Minimum: `GET /healthz` returning 200 OK

### Nginx Routing Strategies
Choose one approach per new service:

**Option 1: Subdomain routing (recommended)**
```
https://service-name.flowbiz.cloud/...
```
- Create DNS A record pointing to VPS IP
- Create `/etc/nginx/conf.d/service-name.flowbiz.cloud.conf`
- Obtain SSL certificate: `sudo certbot certonly --nginx -d service-name.flowbiz.cloud`
- Set `proxy_pass http://127.0.0.1:<SERVICE_PORT>;`

**Option 2: Path-based routing**
```
https://flowbiz.cloud/service-name/...
```
- Add location block to existing `flowbiz.cloud.conf`
- Set `proxy_pass http://127.0.0.1:<SERVICE_PORT>;`
- Use `proxy_set_header X-Script-Name /service-name;` if needed

**Option 3: Separate domain**
```
https://service-name.com/...
```
- Create DNS A record pointing to VPS IP
- Create `/etc/nginx/conf.d/service-name.com.conf`
- Obtain SSL certificate: `sudo certbot certonly --nginx -d service-name.com`
- Set `proxy_pass http://127.0.0.1:<SERVICE_PORT>;`

### Port Allocation (Reserved Ranges)
| Port Range | Usage |
|------------|-------|
| 80, 443 | Reserved for system nginx (public) |
| 8000 | Reserved for flowbiz-ai-core API |
| 5432 | Reserved for flowbiz-ai-core database |
| 8001-8099 | Available for client services (internal) |
| 5433-5499 | Available for client databases (internal) |
| 6379-6399 | Available for Redis/cache (internal) |

**All ports bind to 127.0.0.1 only. System nginx routes public traffic.**

---

## FORBIDDEN ACTIONS (HARD STOP)

### ❌ Do Not Run Nginx in Docker (Production)
**FORBIDDEN:** Running nginx containers in docker-compose for production deployments.

**Reason:** 
- Port 80/443 conflicts across multiple projects
- TLS certificate management complexity
- Routing becomes opaque
- Violates system nginx architecture decision

**Alternative:** Use system nginx with configs in `/etc/nginx/conf.d/`

**Verification:**
```bash
# This command MUST return no results in production
docker ps --filter "name=nginx" --filter "ancestor=nginx"
```

### ❌ Do Not Bind to Public Ports Directly
**FORBIDDEN:** Binding services directly to `0.0.0.0:80` or `0.0.0.0:443` in docker-compose.

**Reason:** 
- Conflicts with system nginx
- No SSL termination
- No security headers
- No centralized routing

**Alternative:** Bind to `127.0.0.1:<PORT>` and route via system nginx

### ❌ Do Not Modify Core Infrastructure Without Authorization
**FORBIDDEN:** Editing global nginx configs or touching flowbiz-ai-core containers.

**Reason:** Breaking nginx or core services affects all projects

**Alternative:** Create isolated nginx configs in `/etc/nginx/conf.d/<your-domain>.conf`

### ❌ Do Not Deploy Client Logic in Core Repo
**FORBIDDEN:** Adding UI code, billing endpoints, or client-specific features to this repository.

**Reason:** This repo is infrastructure and foundational API only

**Alternative:** Create separate client repositories using [CLIENT_PROJECT_TEMPLATE.md](CLIENT_PROJECT_TEMPLATE.md)

### ❌ Do Not Store Secrets in Version Control
**FORBIDDEN:** Committing `.env` files, API keys, passwords, or certificates to Git.

**Reason:** Security vulnerability, credential leakage

**Alternative:** Use `.env.example` as template; manage secrets via environment variables

---

## Troubleshooting Quick Reference

### Check System Nginx
```bash
# Check nginx service status
sudo systemctl status nginx

# Test nginx configuration syntax
sudo nginx -t

# View nginx error logs
sudo tail -f /var/log/nginx/error.log

# View nginx access logs
sudo tail -f /var/log/nginx/access.log

# Reload nginx after config changes
sudo systemctl reload nginx

# Check which ports nginx is listening on
sudo netstat -tlnp | grep nginx
```

### Check Running Docker Containers
```bash
cd /opt/flowbiz/flowbiz-ai-core
docker compose ps
```

**Expected:** API and database services should show `Up` or `Up (healthy)` status. **No nginx container should be present.**

### View Application Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f db

# Last 100 lines
docker compose logs --tail=100 api
```

### Test Localhost Connectivity
```bash
# Test API directly on localhost (from VPS)
curl http://127.0.0.1:8000/healthz

# Test through system nginx (from VPS)
curl http://localhost/healthz
curl https://localhost/healthz -k

# Test public endpoint (from anywhere)
curl https://flowbiz.cloud/healthz
```

### Common Symptoms & Checks

#### Symptom: "502 Bad Gateway"
**Possible Causes:**
- API container not running
- API container crashed
- Database connection failure
- Service not bound to localhost correctly

**Check:**
```bash
# Check API container status
docker compose ps api

# Check API logs
docker compose logs api

# Test API directly on localhost
curl http://127.0.0.1:8000/healthz

# Check nginx upstream configuration
sudo cat /etc/nginx/conf.d/flowbiz.cloud.conf | grep proxy_pass
```

#### Symptom: "SSL certificate not found" or "Certificate error"
**Possible Causes:**
- Certificate expired or not renewed
- Certificate path incorrect in nginx config
- Certbot timer not running

**Check:**
```bash
# Check certbot timer status
sudo systemctl status certbot.timer

# List all certificates
sudo certbot certificates

# Check certificate files
ls -la /etc/letsencrypt/live/flowbiz.cloud/

# Verify certificate in nginx config
sudo grep ssl_certificate /etc/nginx/conf.d/flowbiz.cloud.conf
```

#### Symptom: "Connection refused" on ports 80/443
**Possible Causes:**
- System nginx not running
- Firewall blocking ports
- Nginx config syntax error

**Check:**
```bash
# Check nginx service
sudo systemctl status nginx

# Check nginx config syntax
sudo nginx -t

# Check firewall rules
sudo ufw status

# Check who's listening on ports 80/443
sudo netstat -tlnp | grep -E ':(80|443)'
```

#### Symptom: Database connection errors in API logs
**Possible Causes:**
- Database container not healthy
- Wrong credentials in `.env`
- Database port not accessible on localhost

**Check:**
```bash
# Check database container status
docker compose ps db

# Check database logs
docker compose logs db

# Test database connection
docker compose exec db psql -U flowbiz -d flowbiz -c "SELECT 1;"

# Check port binding
docker compose port db 5432
```

#### Symptom: "nginx container not found" error
**Expected Behavior:** This is correct! There should be **no nginx container** in production.

**Action:** Verify system nginx is running instead:
```bash
sudo systemctl status nginx
sudo netstat -tlnp | grep nginx
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

# Test API directly (localhost)
curl http://127.0.0.1:8000/healthz

# Check system nginx status
sudo systemctl status nginx

# View nginx configuration
sudo cat /etc/nginx/conf.d/flowbiz.cloud.conf
```

### System Nginx Operations

#### Reload Nginx After Config Changes
```bash
# Always test config first
sudo nginx -t

# If test passes, reload
sudo systemctl reload nginx

# Check status
sudo systemctl status nginx
```

#### Add New Domain/Service
```bash
# 1. Copy template
sudo cp /opt/flowbiz/flowbiz-ai-core/nginx/templates/client_system_nginx.conf.template \
     /etc/nginx/conf.d/new-domain.com.conf

# 2. Edit placeholders
sudo nano /etc/nginx/conf.d/new-domain.com.conf
# Replace {{DOMAIN}} with your domain
# Replace {{PORT}} with your service port (e.g., 3001)

# 3. Obtain SSL certificate
sudo certbot certonly --nginx -d new-domain.com

# 4. Test config
sudo nginx -t

# 5. Reload nginx
sudo systemctl reload nginx

# 6. Verify
curl https://new-domain.com/healthz
```

### Rollback Procedures

If a deployment causes issues, use these steps to rollback to a previous stable version:

#### Rollback Service Code (Docker Containers)
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
curl http://127.0.0.1:8000/healthz
curl https://flowbiz.cloud/healthz
```

#### Rollback Nginx Configuration
```bash
# If you have a backup of the working config
sudo cp /etc/nginx/conf.d/flowbiz.cloud.conf.backup /etc/nginx/conf.d/flowbiz.cloud.conf

# Test config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Verify
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
curl http://127.0.0.1:8000/healthz
curl https://flowbiz.cloud/healthz
```

**Important Notes:**
- Always verify health checks after rollback
- Database migrations may need manual intervention if schema changed
- Check logs after rollback: `docker compose logs -f`
- Document the rollback in PR_LOG.md or create an incident report
- System nginx configuration is independent of application code rollbacks

---

## Contact / Ownership

**Maintained by:** FlowBiz Core Team

For questions, issues, or infrastructure changes:
1. **ALWAYS** review mandatory documentation first:
   - [ADR_SYSTEM_NGINX.md](ADR_SYSTEM_NGINX.md) — Architecture decision for system nginx
   - [CODEX_AGENT_BEHAVIOR_LOCK.md](CODEX_AGENT_BEHAVIOR_LOCK.md) — Agent behavior rules
   - [AGENT_NEW_PROJECT_CHECKLIST.md](AGENT_NEW_PROJECT_CHECKLIST.md) — Pre-deployment checklist
   - [AGENT_ONBOARDING.md](AGENT_ONBOARDING.md) — Onboarding guide
2. Check troubleshooting section above
3. If uncertain about infrastructure changes, **STOP** and propose a doc-only PR first
4. **DO NOT** make destructive changes without approval
5. When in doubt → **document first, deploy later**

---

## Related Documentation

### Infrastructure Rules (MANDATORY READING)
- **[ADR_SYSTEM_NGINX.md](ADR_SYSTEM_NGINX.md)** — Architecture decision record for system nginx (NON-NEGOTIABLE)
- **[CODEX_AGENT_BEHAVIOR_LOCK.md](CODEX_AGENT_BEHAVIOR_LOCK.md)** — Agent behavior rules and safety locks
- **[CODEX_SYSTEM_NGINX_FIRST.md](CODEX_SYSTEM_NGINX_FIRST.md)** — System nginx operational guide
- **[AGENT_NEW_PROJECT_CHECKLIST.md](AGENT_NEW_PROJECT_CHECKLIST.md)** — Pre-deployment checklist (MUST complete before deploy)

### Deployment & Operations
- **[DEPLOYMENT_VPS.md](DEPLOYMENT_VPS.md)** — Step-by-step VPS deployment instructions
- **[AGENT_ONBOARDING.md](AGENT_ONBOARDING.md)** — Quick start for new agents deploying services
- **[CLIENT_PROJECT_TEMPLATE.md](CLIENT_PROJECT_TEMPLATE.md)** — Template for new service projects

### Architecture & History
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — System design and technical architecture
- **[PR_LOG.md](PR_LOG.md)** — Historical record of all changes

---

## Architecture Compliance Checklist

Before deploying or modifying infrastructure, verify:

- [ ] **No nginx containers running:** `docker ps | grep nginx` returns nothing
- [ ] **System nginx owns ports 80/443:** `sudo netstat -tlnp | grep nginx` shows nginx process
- [ ] **Services bind to localhost only:** Check docker-compose port mappings use `127.0.0.1:<PORT>`
- [ ] **Nginx configs in /etc/nginx/conf.d/:** One file per domain
- [ ] **SSL certificates managed by Certbot:** Check `/etc/letsencrypt/live/`
- [ ] **All routing through system nginx:** No direct public port bindings
- [ ] **Pre-deployment checklist completed:** See [AGENT_NEW_PROJECT_CHECKLIST.md](AGENT_NEW_PROJECT_CHECKLIST.md)

---

**Document Version:** 2.0 (Updated for System Nginx Architecture)  
**VPS Architecture:** Multi-Project with System Nginx  
**Last Major Update:** 2025-12-26 — Aligned with system nginx mandatory architecture
