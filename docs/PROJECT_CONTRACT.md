# Project Contract — Client Services on Shared FlowBiz VPS

## Purpose

This document defines the **mandatory integration contract** between client projects and the FlowBiz shared VPS infrastructure. All client services MUST comply with this contract to be deployable on the shared environment.

**CRITICAL:** This contract is NON-NEGOTIABLE. Non-compliant services will be rejected at deployment time.

---

## Prerequisites — MANDATORY Reading

Before implementing any client service, you **MUST** read these documents in order:

1. **[ADR_SYSTEM_NGINX.md](./ADR_SYSTEM_NGINX.md)** — Architectural decision: Why system nginx is the only allowed reverse proxy
2. **[AGENT_NEW_PROJECT_CHECKLIST.md](./AGENT_NEW_PROJECT_CHECKLIST.md)** — Pre-deployment checklist (ALL items must be YES)
3. **[CODEX_AGENT_BEHAVIOR_LOCK.md](./CODEX_AGENT_BEHAVIOR_LOCK.md)** — Agent behavior rules and safety locks

**If any checklist item is NO → DEPLOYMENT IS FORBIDDEN**

---

## API Contract

### Required Endpoints (MANDATORY)

Every client service MUST expose these two endpoints:

#### 1. Health Check Endpoint

```http
GET /healthz
```

**Response:**
```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "ok",
  "service": "<service-name>",
  "version": "<semver>"
}
```

**Purpose:** Load balancer health checks and uptime monitoring

**Requirements:**
- MUST return `200 OK` when service is healthy
- MUST respond within 3 seconds
- MUST NOT require authentication
- MUST be available even if dependencies (database, external APIs) are degraded

#### 2. Metadata Endpoint

```http
GET /v1/meta
```

**Response:**
```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "service": "<service-name>",
  "environment": "dev|staging|prod",
  "version": "<semver>",
  "build_sha": "<git-commit-sha>"
}
```

**Purpose:** Runtime metadata for observability and debugging

**Requirements:**
- MUST return `200 OK`
- MUST include all four fields
- MUST read version from `FLOWBIZ_VERSION` environment variable
- MUST read build_sha from `FLOWBIZ_BUILD_SHA` environment variable (or default to "local-dev")
- MUST NOT require authentication

---

## Environment Variables Contract

### Naming Convention (STRICT)

Client services MUST follow this environment variable naming scheme:

#### APP_* Prefix (Application Settings)
Required for application-specific configuration:

```bash
APP_SERVICE_NAME=<service-name>       # Service identifier
APP_ENV=dev|staging|prod              # Environment identifier
APP_LOG_LEVEL=DEBUG|INFO|WARNING|ERROR  # Logging verbosity
APP_CORS_ORIGINS=["http://localhost:3000"]  # Allowed CORS origins (JSON array)
```

#### FLOWBIZ_* Prefix (Metadata)
Required for versioning and build information:

```bash
FLOWBIZ_VERSION=0.1.0                 # Semantic version
FLOWBIZ_BUILD_SHA=abc123def           # Git commit SHA
```

#### Integration (If connecting to FlowBiz AI Core)
Optional, but if integrating with core:

```bash
FLOWBIZ_CORE_URL=http://localhost:8000
FLOWBIZ_API_KEY=<api-key>
```

**Validation:**
- Services MUST validate all required `APP_*` variables at startup
- Services MUST fail fast (exit with error) if required variables are missing
- Services MUST expose `FLOWBIZ_VERSION` and `FLOWBIZ_BUILD_SHA` via `/v1/meta`

---

## Port Binding Contract (CRITICAL)

### HARD RULE: Localhost-Only Binding

All services MUST bind to localhost ports ONLY. This is NON-NEGOTIABLE.

**Docker Compose Configuration:**

```yaml
services:
  app:
    build: .
    ports:
      - "127.0.0.1:<PORT>:<PORT>"  # ✅ CORRECT: Localhost only
    # NOT:
    # - "0.0.0.0:<PORT>:<PORT>"    # ❌ FORBIDDEN: Public binding
    # - "<PORT>:<PORT>"             # ❌ FORBIDDEN: Defaults to 0.0.0.0
```

**Port Allocation:**
- Ports 80, 443: Reserved for system nginx
- Ports 5432, 6379, 3306: Reserved for shared databases
- Port 8000: Reserved for flowbiz-ai-core
- Port 3001+: Available for client services
- Port 8001+: Available for client services

**Verification:**
```bash
# Service MUST respond on localhost
curl http://127.0.0.1:<PORT>/healthz
# Expected: 200 OK

# Service MUST NOT be accessible from outside
curl http://<VPS-IP>:<PORT>/healthz
# Expected: Connection refused
```

---

## Nginx Routing Contract

### System Nginx is the ONLY Reverse Proxy

**MANDATORY RULES:**

1. **NO Docker nginx containers** in docker-compose.yml (production)
2. **NO ingress controllers** (Traefik, Caddy, etc.)
3. **NO embedded reverse proxies** within your application
4. **ONE service = ONE port = ONE domain** (configured externally via system nginx)

**Routing Configuration:**
- System nginx routes `https://<domain>` → `http://127.0.0.1:<PORT>`
- Nginx configuration is managed externally in `/etc/nginx/conf.d/`
- Client projects MUST NOT include nginx configurations in their repository

**Template:**
Use `nginx/templates/client_system_nginx.conf.template` as reference, but:
- ✅ You MAY document the expected nginx configuration in your README
- ❌ You MUST NOT deploy nginx configurations yourself
- ❌ You MUST NOT restart or reload system nginx
- ✅ Infrastructure team will deploy nginx configuration after service verification

---

## Security Headers Contract

System nginx applies the following security headers to all responses:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

**Requirements:**
- Client services MUST NOT override or remove these headers
- Client services MAY add additional security headers if needed
- Content-Security-Policy (CSP) can be configured per-path if required

---

## Error Response Contract

All error responses MUST follow this format:

```json
{
  "detail": "Human-readable error message",
  "request_id": "uuid-or-trace-id",
  "timestamp": "2025-12-26T10:30:00Z"
}
```

**Standard HTTP Status Codes:**
- `400` — Bad Request (client error, invalid input)
- `401` — Unauthorized (authentication required)
- `403` — Forbidden (authenticated but insufficient permissions)
- `404` — Not Found
- `422` — Validation Error (structured validation failures)
- `500` — Internal Server Error
- `502` — Bad Gateway (upstream dependency failure)
- `503` — Service Unavailable (temporary unavailability)

---

## Logging Contract

### Structured Logging (Required)

All logs MUST be JSON-formatted for centralized aggregation:

```json
{
  "timestamp": "2025-12-26T10:30:00Z",
  "level": "INFO|WARNING|ERROR",
  "service": "<service-name>",
  "request_id": "uuid",
  "message": "Human-readable message",
  "context": {
    "key": "value"
  }
}
```

**Required Fields:**
- `timestamp` — ISO 8601 format with timezone
- `level` — Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `service` — Service name (from `APP_SERVICE_NAME`)
- `request_id` — Trace ID for request correlation
- `message` — Human-readable log message

**Best Practices:**
- Use `request_id` consistently across all logs for a single request
- Log at appropriate levels (INFO for normal operations, WARNING for degraded state, ERROR for failures)
- Include context data (user_id, endpoint, duration) when relevant

---

## Docker Container Contract

### Required Files

```
.
├── Dockerfile                    # Container build definition
├── docker-compose.yml            # Development compose file
├── docker-compose.prod.yml       # Production overrides
├── .env.example                  # Environment variable template
└── .dockerignore                 # Build context exclusions
```

### Dockerfile Requirements

```dockerfile
FROM python:3.11-slim  # Or appropriate base image

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose internal port (documentation only)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8000/healthz || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Requirements:**
- MUST use official base images from Docker Hub
- MUST include a HEALTHCHECK instruction
- MUST NOT run as root user (use `USER` instruction)
- MUST use multi-stage builds when possible to minimize image size

### Docker Compose Requirements (Development)

```yaml
version: "3.9"

services:
  app:
    build: .
    ports:
      - "127.0.0.1:3001:8000"  # localhost:external -> container:internal
    environment:
      APP_SERVICE_NAME: ${APP_SERVICE_NAME}
      APP_ENV: ${APP_ENV}
      APP_LOG_LEVEL: ${APP_LOG_LEVEL}
      APP_CORS_ORIGINS: ${APP_CORS_ORIGINS}
      FLOWBIZ_VERSION: ${FLOWBIZ_VERSION}
      FLOWBIZ_BUILD_SHA: ${FLOWBIZ_BUILD_SHA}
    volumes:
      - ./app:/app/app  # Hot reload for development
```

### Docker Compose Requirements (Production)

```yaml
version: "3.9"

services:
  app:
    restart: always
    environment:
      APP_ENV: prod
      APP_LOG_LEVEL: WARNING
    # Remove volume mounts for production
```

**Verification:**
```bash
# Development
docker compose up --build
curl http://127.0.0.1:3001/healthz

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
curl http://127.0.0.1:3001/healthz
```

---

## Deployment Flow (MANDATORY)

### Step 1: Local Verification

```bash
# Start service
docker compose up --build -d

# Verify health
curl http://127.0.0.1:<PORT>/healthz
# Expected: {"status": "ok", ...}

# Verify metadata
curl http://127.0.0.1:<PORT>/v1/meta
# Expected: {"service": "...", "version": "...", ...}
```

### Step 2: VPS Deployment (Service Only)

```bash
# On VPS
cd /opt/projects/<service-name>
git pull origin main
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify localhost access
curl http://127.0.0.1:<PORT>/healthz
# Expected: 200 OK
```

### Step 3: Request Nginx Configuration (After Service Verification)

**ONLY AFTER** service responds successfully on localhost:

1. Create documentation showing expected nginx configuration
2. Request infrastructure team to deploy nginx configuration
3. Infrastructure team will:
   - Copy template from `nginx/templates/client_system_nginx.conf.template`
   - Replace `{{DOMAIN}}` and `{{PORT}}` placeholders
   - Deploy to `/etc/nginx/conf.d/<domain>.conf`
   - Test: `sudo nginx -t`
   - Reload: `sudo systemctl reload nginx`

### Step 4: Public HTTPS Verification (LAST STEP)

```bash
# After nginx configuration is deployed
curl https://<domain>/healthz
# Expected: 200 OK

# Verify security headers
curl -I https://<domain>/healthz
# Expected: X-Content-Type-Options, X-Frame-Options, HSTS, etc.
```

---

## Forbidden Actions (NEVER DO THIS)

### ❌ ABSOLUTE PROHIBITIONS

1. **Docker nginx containers in production**
   ```yaml
   # ❌ FORBIDDEN
   services:
     nginx:
       image: nginx
       ports:
         - "80:80"
   ```

2. **Public port binding (0.0.0.0)**
   ```yaml
   # ❌ FORBIDDEN
   services:
     app:
       ports:
         - "0.0.0.0:3001:8000"
         - "3001:8000"  # Defaults to 0.0.0.0
   ```

3. **Modifying system nginx configuration**
   ```bash
   # ❌ FORBIDDEN
   sudo nano /etc/nginx/conf.d/other-service.conf
   sudo systemctl reload nginx
   ```

4. **Making assumptions about VPS layout**
   - ❌ Assuming specific directory paths
   - ❌ Assuming available ports without checking
   - ❌ Assuming other services' endpoints or ports

5. **Deploying without health checks**
   ```bash
   # ❌ FORBIDDEN: Deploying without verifying /healthz works
   docker compose up -d  # Without testing first
   ```

---

## Fail-Safe Protocol

### When to STOP and Escalate

If you are **UNSURE** about any of the following:

- ✋ Port allocation (which port to use?)
- ✋ Domain configuration (what domain should be used?)
- ✋ Nginx behavior (how will routing work?)
- ✋ Multi-project impact (will this affect other services?)
- ✋ Any checklist item in `AGENT_NEW_PROJECT_CHECKLIST.md` is NO

**THEN YOU MUST:**

1. ❌ **STOP** all deployment activities immediately
2. 📝 **DOCUMENT** your intended changes in a proposal
3. 🚨 **ESCALATE** via GitHub issue or documentation-only PR
4. ⏸️ **WAIT** for infrastructure team review and approval

**DO NOT:**
- ❌ "Try and see" on production infrastructure
- ❌ Make assumptions about how things "should work"
- ❌ Deploy first and ask questions later

---

## Success Criteria

A client service deployment is considered **SUCCESSFUL** only if:

- ✅ Service responds `200 OK` to `curl http://127.0.0.1:<PORT>/healthz`
- ✅ Service responds `200 OK` to `curl http://127.0.0.1:<PORT>/v1/meta`
- ✅ Service is NOT accessible from outside (public IP)
- ✅ No other services are affected or disrupted
- ✅ No nginx containers exist in `docker ps`
- ✅ System nginx owns ports 80/443 only
- ✅ All environment variables are documented in `.env.example`
- ✅ No secrets are committed to git
- ✅ Service can be stopped with `docker compose down` without affecting other services

---

## Compliance Verification

### Pre-Deployment Checklist Reference

Before deploying, verify ALL items in:
- **[AGENT_NEW_PROJECT_CHECKLIST.md](./AGENT_NEW_PROJECT_CHECKLIST.md)**

### Post-Deployment Verification

```bash
# 1. No nginx containers
docker ps --filter "ancestor=nginx"
# Expected: No results

# 2. System nginx owns 80/443
sudo netstat -tlnp | grep ':80\|:443'
# Expected: nginx process only

# 3. Service accessible on localhost
curl http://127.0.0.1:<PORT>/healthz
# Expected: 200 OK

# 4. Service NOT accessible externally (before nginx config)
curl http://<VPS-IP>:<PORT>/healthz
# Expected: Connection refused

# 5. After nginx configuration: HTTPS works
curl https://<domain>/healthz
# Expected: 200 OK

# 6. Security headers present
curl -I https://<domain>/healthz | grep -i "x-frame-options"
# Expected: X-Frame-Options: DENY
```

---

## Documentation Requirements

Every client project repository MUST include:

```
docs/
├── PROJECT_CONTRACT.md     # This contract (copy or reference)
├── DEPLOYMENT.md           # Deployment-specific instructions
└── GUARDRAILS.md           # Development guidelines (copy from core)

README.md                   # Quick start, endpoints, environment variables
.env.example                # All required environment variables (no secrets)
```

**README.md Minimum Content:**
- Service name and purpose
- Required environment variables
- How to run locally
- How to run in production
- Health check endpoints
- Integration points (if any)

**DEPLOYMENT.md Minimum Content:**
- Prerequisites (VPS access, domain, SSL)
- Deployment steps
- Verification commands
- Rollback procedure

---

## Version History

- **v1.0** — 2025-12-26 — Initial project contract definition
- Status: **ACTIVE** (Enforced for all new client projects)

---

## References

- **[ADR_SYSTEM_NGINX.md](./ADR_SYSTEM_NGINX.md)** — Architecture decision record
- **[AGENT_NEW_PROJECT_CHECKLIST.md](./AGENT_NEW_PROJECT_CHECKLIST.md)** — Pre-deployment checklist
- **[CODEX_AGENT_BEHAVIOR_LOCK.md](./CODEX_AGENT_BEHAVIOR_LOCK.md)** — Agent behavior rules
- **[GUARDRAILS.md](./GUARDRAILS.md)** — Development guidelines

---

**Maintained by:** FlowBiz Infrastructure Team  
**Contact:** Create GitHub issue with `infrastructure` label for questions or clarifications
