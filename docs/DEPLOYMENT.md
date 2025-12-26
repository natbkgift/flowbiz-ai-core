# Deployment Guide — Client Projects on Shared FlowBiz VPS

## Purpose

This guide provides step-by-step deployment instructions for client services on the shared FlowBiz VPS. It is designed for agents and developers who are deploying services that comply with the FlowBiz infrastructure standards.

**CRITICAL:** This guide assumes you have read and understood:
1. **[ADR_SYSTEM_NGINX.md](./ADR_SYSTEM_NGINX.md)** — Why system nginx is mandatory
2. **[AGENT_NEW_PROJECT_CHECKLIST.md](./AGENT_NEW_PROJECT_CHECKLIST.md)** — Pre-deployment checklist
3. **[PROJECT_CONTRACT.md](./PROJECT_CONTRACT.md)** — API and integration contract

**If you haven't read these documents, STOP and read them first.**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [VPS Deployment](#vps-deployment)
4. [Nginx Configuration](#nginx-configuration)
5. [SSL/TLS Setup](#ssltls-setup)
6. [Verification](#verification)
7. [Rollback](#rollback)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Infrastructure

- **VPS:** Ubuntu 24.04 LTS
- **Docker:** Version 24.0+
- **Docker Compose:** Version 2.20+
- **System Nginx:** Version 1.18+ (managed via systemd)
- **Let's Encrypt:** Certbot for SSL certificate management

### Required Access

- SSH access to VPS (key-based authentication only)
- Git access to service repository
- Environment variables documented in `.env.example`
- Allocated port number (coordinated with infrastructure team)

### Required Documentation

Your service repository MUST have:
- `README.md` — Service description, setup, and usage
- `.env.example` — All required environment variables (no secrets)
- `docker-compose.yml` — Development configuration
- `docker-compose.prod.yml` — Production overrides
- `Dockerfile` — Container build definition

---

## Local Development

### 1. Clone Repository

```bash
git clone https://github.com/<org>/<service-repo>.git
cd <service-repo>
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

**Required Variables:**
```bash
APP_SERVICE_NAME=my-service
APP_ENV=dev
APP_LOG_LEVEL=DEBUG
APP_CORS_ORIGINS=["http://localhost:3000"]

FLOWBIZ_VERSION=0.1.0
FLOWBIZ_BUILD_SHA=local-dev
```

### 3. Start Service (Development)

```bash
# Build and start
docker compose up --build

# Or run in background
docker compose up --build -d

# View logs
docker compose logs -f
```

### 4. Verify Local Service

```bash
# Health check
curl http://127.0.0.1:<PORT>/healthz
# Expected: {"status": "ok", "service": "...", "version": "..."}

# Metadata
curl http://127.0.0.1:<PORT>/v1/meta
# Expected: {"service": "...", "environment": "dev", "version": "...", "build_sha": "..."}

# Test business endpoints (if applicable)
curl -X POST http://127.0.0.1:<PORT>/v1/resource \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

### 5. Stop Service

```bash
docker compose down
```

---

## VPS Deployment

### Step-by-Step Deployment Process

#### Step 1: Prepare Production Environment

```bash
# SSH into VPS
ssh user@<vps-ip>

# Navigate to projects directory
cd /opt/projects

# Clone repository (first time only)
git clone https://github.com/<org>/<service-repo>.git
cd <service-repo>

# Or update existing repository
cd /opt/projects/<service-repo>
git pull origin main
```

#### Step 2: Configure Production Environment

```bash
# Copy environment template
cp .env.example .env.prod

# Edit with production values
nano .env.prod
```

**Production Environment Variables:**
```bash
APP_SERVICE_NAME=my-service
APP_ENV=prod
APP_LOG_LEVEL=WARNING
APP_CORS_ORIGINS=["https://my-domain.flowbiz.cloud"]

FLOWBIZ_VERSION=0.1.0
FLOWBIZ_BUILD_SHA=$(git rev-parse --short HEAD)

# Integration (if needed)
FLOWBIZ_CORE_URL=http://127.0.0.1:8000
FLOWBIZ_API_KEY=<production-api-key>

# Database (if needed)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

**Security:**
```bash
# Restrict environment file permissions
chmod 600 .env.prod
```

#### Step 3: Start Service

```bash
# Start with production configuration
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

# Check container status
docker compose ps

# View logs
docker compose logs -f
```

#### Step 4: Verify Service on Localhost

**CRITICAL:** Service MUST work on localhost before requesting nginx configuration.

```bash
# Health check
curl http://127.0.0.1:<PORT>/healthz
# Expected: 200 OK {"status": "ok", ...}

# Metadata
curl http://127.0.0.1:<PORT>/v1/meta
# Expected: 200 OK {"service": "...", "environment": "prod", ...}

# Verify service is NOT publicly accessible (expected)
curl http://<vps-ip>:<PORT>/healthz
# Expected: Connection refused (this is correct - localhost binding working)
```

**If health checks fail:**
- Check container logs: `docker compose logs`
- Check environment variables: `docker compose config`
- Verify port binding: `docker compose ps`
- Check database connectivity (if applicable)

**DO NOT PROCEED** to nginx configuration until localhost health checks pass.

---

## Nginx Configuration

### IMPORTANT: Infrastructure Team Only

**Client projects MUST NOT:**
- ❌ Create nginx configuration files themselves
- ❌ Deploy nginx configurations to `/etc/nginx/conf.d/`
- ❌ Restart or reload nginx
- ❌ Modify existing nginx configurations for other services

**Client projects MAY:**
- ✅ Document expected nginx configuration in their README
- ✅ Request nginx configuration via GitHub issue or infrastructure team
- ✅ Provide domain name and port number

### Request Process

After verifying service works on localhost:

1. **Create GitHub Issue** with `infrastructure` label:
   ```markdown
   Title: Nginx Configuration Request for <service-name>

   ## Service Details
   - Service Name: my-service
   - Domain: my-service.flowbiz.cloud
   - Port: 3001
   - Repository: https://github.com/org/repo

   ## Verification
   - [x] Service responds to curl http://127.0.0.1:3001/healthz
   - [x] Service responds to curl http://127.0.0.1:3001/v1/meta
   - [x] Container is running: docker compose ps
   - [x] Environment variables configured

   ## Template
   Using: nginx/templates/client_system_nginx.conf.template
   Replacements: {{DOMAIN}} = my-service.flowbiz.cloud, {{PORT}} = 3001
   ```

2. **Infrastructure team will:**
   - Review service deployment
   - Copy template from `nginx/templates/client_system_nginx.conf.template`
   - Replace placeholders: `{{DOMAIN}}` and `{{PORT}}`
   - Deploy to `/etc/nginx/conf.d/<domain>.conf`
   - Test configuration: `sudo nginx -t`
   - Reload nginx: `sudo systemctl reload nginx`
   - Verify HTTPS access

3. **You will be notified** when nginx configuration is deployed

### Expected Nginx Configuration (Reference Only)

This is what the infrastructure team will deploy:

```nginx
# HTTP -> HTTPS redirect
server {
  listen 80;
  server_name my-service.flowbiz.cloud;
  server_tokens off;

  location /.well-known/acme-challenge/ {
    root /var/www/certbot;
  }

  location / {
    return 301 https://$host$request_uri;
  }
}

# HTTPS server
server {
  listen 443 ssl http2;
  server_name my-service.flowbiz.cloud;
  server_tokens off;

  # SSL certificates
  ssl_certificate /etc/letsencrypt/live/my-service.flowbiz.cloud/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/my-service.flowbiz.cloud/privkey.pem;

  # SSL configuration
  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_ciphers HIGH:!aNULL:!MD5;
  ssl_prefer_server_ciphers on;

  # Security headers
  add_header X-Content-Type-Options "nosniff" always;
  add_header X-Frame-Options "DENY" always;
  add_header Referrer-Policy "strict-origin-when-cross-origin" always;
  add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

  # Proxy to localhost service
  location / {
    proxy_pass http://127.0.0.1:3001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```

---

## SSL/TLS Setup

### Let's Encrypt Certificate Management

SSL certificates are managed by the infrastructure team using Certbot.

**Infrastructure team will:**

1. **Obtain certificate** (first time):
   ```bash
   sudo certbot certonly --nginx -d my-service.flowbiz.cloud
   ```

2. **Verify certificate paths**:
   ```bash
   ls -la /etc/letsencrypt/live/my-service.flowbiz.cloud/
   # fullchain.pem
   # privkey.pem
   ```

3. **Auto-renewal** is configured via cron:
   ```bash
   # Certbot auto-renewal (runs twice daily)
   0 0,12 * * * certbot renew --quiet --deploy-hook "systemctl reload nginx"
   ```

**Certificate Renewal:**
- Automatic renewal occurs 30 days before expiration
- Nginx is automatically reloaded after renewal
- No client service action required

**Troubleshooting SSL:**
- Certificate not found: Check domain DNS (A record)
- Certificate expired: Infrastructure team will renew manually if auto-renewal failed
- Mixed content warnings: Ensure all resources loaded over HTTPS

---

## Verification

### Post-Deployment Checks

After nginx configuration is deployed, verify public HTTPS access:

#### 1. HTTPS Health Check

```bash
curl https://my-service.flowbiz.cloud/healthz
# Expected: 200 OK {"status": "ok", ...}
```

#### 2. HTTPS Metadata

```bash
curl https://my-service.flowbiz.cloud/v1/meta
# Expected: 200 OK {"service": "...", "environment": "prod", ...}
```

#### 3. Security Headers

```bash
curl -I https://my-service.flowbiz.cloud/healthz

# Expected headers:
# HTTP/2 200
# x-content-type-options: nosniff
# x-frame-options: DENY
# referrer-policy: strict-origin-when-cross-origin
# permissions-policy: geolocation=(), microphone=(), camera=()
# strict-transport-security: max-age=31536000; includeSubDomains
```

#### 4. HTTP to HTTPS Redirect

```bash
curl -I http://my-service.flowbiz.cloud/healthz
# Expected: 301 Moved Permanently
# Location: https://my-service.flowbiz.cloud/healthz
```

#### 5. SSL Certificate Validity

```bash
echo | openssl s_client -servername my-service.flowbiz.cloud -connect my-service.flowbiz.cloud:443 2>/dev/null | openssl x509 -noout -dates

# Expected output:
# notBefore=<date>
# notAfter=<date in future>
```

#### 6. Service Container Status

```bash
# On VPS
docker compose ps

# Expected: service is "Up" and healthy
```

#### 7. No Port Conflicts

```bash
# Verify no nginx containers
docker ps --filter "ancestor=nginx"
# Expected: No results

# Verify system nginx owns 80/443
sudo netstat -tlnp | grep ':80\|:443'
# Expected: nginx process only
```

### Smoke Test Business Endpoints

Test critical business functionality:

```bash
# Example: Create resource
curl -X POST https://my-service.flowbiz.cloud/v1/resource \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"name": "test"}'

# Example: Get resource
curl https://my-service.flowbiz.cloud/v1/resource/123
```

---

## Rollback

### Rollback Procedure

If deployment fails or causes issues:

#### 1. Stop Service

```bash
cd /opt/projects/<service-repo>
docker compose down
```

#### 2. Revert to Previous Version

```bash
# Find previous working commit
git log --oneline -n 5

# Revert to previous commit
git checkout <previous-commit-sha>

# Restart service
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

#### 3. Verify Rollback

```bash
# Check service health
curl http://127.0.0.1:<PORT>/healthz

# Check public access
curl https://my-service.flowbiz.cloud/healthz
```

#### 4. Remove Nginx Configuration (If Needed)

**Only infrastructure team:**
```bash
sudo rm /etc/nginx/conf.d/my-service.flowbiz.cloud.conf
sudo nginx -t
sudo systemctl reload nginx
```

### Emergency Rollback

If service is causing critical issues:

```bash
# Immediate stop
docker compose down

# Disable nginx configuration (infrastructure team only)
sudo mv /etc/nginx/conf.d/my-service.flowbiz.cloud.conf \
       /etc/nginx/conf.d/my-service.flowbiz.cloud.conf.disabled
sudo systemctl reload nginx
```

---

## Troubleshooting

### Common Issues

#### Issue: Service container fails to start

**Symptoms:**
```bash
docker compose ps
# Status: Exited (1)
```

**Diagnosis:**
```bash
# Check logs
docker compose logs

# Check environment variables
docker compose config

# Verify .env.prod exists and is readable
cat .env.prod
```

**Solution:**
- Fix environment variable syntax errors
- Ensure all required variables are set
- Check database connection strings (if applicable)
- Verify file permissions: `chmod 600 .env.prod`

---

#### Issue: Health check returns connection refused

**Symptoms:**
```bash
curl http://127.0.0.1:3001/healthz
# curl: (7) Failed to connect to 127.0.0.1 port 3001: Connection refused
```

**Diagnosis:**
```bash
# Check if container is running
docker compose ps

# Check if service is listening on correct port
docker compose exec app netstat -tlnp

# Check docker-compose port binding
docker compose config | grep ports
```

**Solution:**
- Verify container is running: `docker compose up -d`
- Check port binding in docker-compose.yml: `127.0.0.1:3001:8000`
- Ensure application listens on `0.0.0.0:8000` inside container (not `127.0.0.1:8000`)
- Check container logs for startup errors

---

#### Issue: Service accessible on localhost but not via HTTPS

**Symptoms:**
```bash
curl http://127.0.0.1:3001/healthz
# 200 OK (works)

curl https://my-service.flowbiz.cloud/healthz
# Connection refused or timeout
```

**Diagnosis:**
```bash
# Check if nginx configuration exists
ls -la /etc/nginx/conf.d/my-service.flowbiz.cloud.conf

# Check nginx syntax
sudo nginx -t

# Check nginx is running
sudo systemctl status nginx

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log
```

**Solution:**
- Verify nginx configuration was deployed
- Check domain DNS resolves to VPS IP: `nslookup my-service.flowbiz.cloud`
- Verify SSL certificate exists: `ls -la /etc/letsencrypt/live/my-service.flowbiz.cloud/`
- Request infrastructure team to verify nginx configuration

---

#### Issue: 502 Bad Gateway

**Symptoms:**
```bash
curl https://my-service.flowbiz.cloud/healthz
# 502 Bad Gateway
```

**Diagnosis:**
```bash
# Check service is running
docker compose ps

# Check service responds on localhost
curl http://127.0.0.1:3001/healthz

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log
```

**Solution:**
- Service container not running: `docker compose up -d`
- Wrong port in nginx config: Verify proxy_pass matches service port
- Service crashed: Check `docker compose logs`
- Firewall blocking localhost: Highly unlikely, check `iptables -L`

---

#### Issue: Missing security headers

**Symptoms:**
```bash
curl -I https://my-service.flowbiz.cloud/healthz
# Missing: X-Frame-Options, HSTS, etc.
```

**Diagnosis:**
```bash
# Check nginx configuration
sudo cat /etc/nginx/conf.d/my-service.flowbiz.cloud.conf | grep add_header
```

**Solution:**
- Nginx configuration missing security headers
- Infrastructure team will update configuration using template
- Verify template was used: `nginx/templates/client_system_nginx.conf.template`

---

#### Issue: Port conflict

**Symptoms:**
```bash
docker compose up -d
# Error: port is already allocated
```

**Diagnosis:**
```bash
# Check what's using the port
sudo netstat -tlnp | grep :3001

# Check other docker containers
docker ps
```

**Solution:**
- Another service is using the port
- Coordinate with infrastructure team for new port allocation
- Update docker-compose.yml with new port
- Update documentation with correct port

---

### Getting Help

If you cannot resolve an issue:

1. **Check Documentation:**
   - [ADR_SYSTEM_NGINX.md](./ADR_SYSTEM_NGINX.md)
   - [AGENT_NEW_PROJECT_CHECKLIST.md](./AGENT_NEW_PROJECT_CHECKLIST.md)
   - [PROJECT_CONTRACT.md](./PROJECT_CONTRACT.md)

2. **Create GitHub Issue:**
   ```markdown
   Title: Deployment Issue: <brief description>

   ## Service Details
   - Service Name: my-service
   - Domain: my-service.flowbiz.cloud
   - Port: 3001

   ## Issue Description
   <Describe the problem>

   ## Steps to Reproduce
   1. Step 1
   2. Step 2

   ## Expected Behavior
   <What should happen>

   ## Actual Behavior
   <What actually happens>

   ## Logs
   ```bash
   <Paste relevant logs>
   ```

   ## Troubleshooting Attempted
   - [x] Checked container status
   - [x] Checked service logs
   - [ ] Checked nginx logs (infrastructure team access required)
   ```

3. **Label Issue:** Add `infrastructure` label for infrastructure team attention

4. **Contact Infrastructure Team:** For urgent production issues

---

## Deployment Checklist

Before considering deployment complete:

- [ ] Service responds to `curl http://127.0.0.1:<PORT>/healthz` with 200 OK
- [ ] Service responds to `curl http://127.0.0.1:<PORT>/v1/meta` with 200 OK
- [ ] Service container is running: `docker compose ps`
- [ ] Environment variables configured in `.env.prod`
- [ ] Environment file permissions set: `chmod 600 .env.prod`
- [ ] Nginx configuration requested via GitHub issue
- [ ] Nginx configuration deployed by infrastructure team
- [ ] SSL certificate obtained for domain
- [ ] Service responds to `curl https://<domain>/healthz` with 200 OK
- [ ] Security headers present in HTTPS response
- [ ] HTTP redirects to HTTPS
- [ ] Business endpoints smoke tested
- [ ] No nginx containers in `docker ps`
- [ ] System nginx owns ports 80/443 only
- [ ] No other services affected
- [ ] Rollback plan documented

---

## References

- **[ADR_SYSTEM_NGINX.md](./ADR_SYSTEM_NGINX.md)** — Architecture decision record
- **[AGENT_NEW_PROJECT_CHECKLIST.md](./AGENT_NEW_PROJECT_CHECKLIST.md)** — Pre-deployment checklist
- **[PROJECT_CONTRACT.md](./PROJECT_CONTRACT.md)** — API and integration contract
- **[CODEX_AGENT_BEHAVIOR_LOCK.md](./CODEX_AGENT_BEHAVIOR_LOCK.md)** — Agent behavior rules
- **[GUARDRAILS.md](./GUARDRAILS.md)** — Development guidelines

---

**Version:** 1.0  
**Last Updated:** 2025-12-26  
**Maintained by:** FlowBiz Infrastructure Team
