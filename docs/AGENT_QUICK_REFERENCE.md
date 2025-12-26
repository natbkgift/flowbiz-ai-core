# Client Project Quick Reference — Agent Deployment Guide

## 🚨 CRITICAL: Read These First (In Order)

1. **[ADR_SYSTEM_NGINX.md](./ADR_SYSTEM_NGINX.md)** — Why system nginx is mandatory
2. **[AGENT_NEW_PROJECT_CHECKLIST.md](./AGENT_NEW_PROJECT_CHECKLIST.md)** — Pre-deployment checklist
3. **[PROJECT_CONTRACT.md](./PROJECT_CONTRACT.md)** — API and integration contract
4. **[DEPLOYMENT.md](./DEPLOYMENT.md)** — Step-by-step deployment guide

**If ANY checklist item is NO → DEPLOYMENT IS FORBIDDEN**

---

## ⚡ Quick Rules (Non-Negotiable)

### Port Binding
```yaml
# ✅ CORRECT
ports:
  - "127.0.0.1:3001:8000"

# ❌ FORBIDDEN
ports:
  - "0.0.0.0:3001:8000"
  - "3001:8000"
```

### Reverse Proxy
- ✅ System nginx (managed via systemd) is the ONLY reverse proxy
- ❌ NO Docker nginx in docker-compose.yml (production)
- ❌ NO Traefik, Caddy, or any other ingress controllers
- ❌ NO embedded reverse proxies in your application

### Required Endpoints
```bash
# Health check
GET /healthz
# Response: {"status": "ok", "service": "...", "version": "..."}

# Metadata
GET /v1/meta
# Response: {"service": "...", "environment": "...", "version": "...", "build_sha": "..."}
```

### Environment Variables
```bash
# Application settings (required)
APP_SERVICE_NAME=my-service
APP_ENV=dev|staging|prod
APP_LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
APP_CORS_ORIGINS=["http://localhost:3000"]

# Metadata (required)
FLOWBIZ_VERSION=0.1.0
FLOWBIZ_BUILD_SHA=abc123def
```

---

## 📋 Deployment Checklist (Quick)

### Before Deploy
- [ ] Service responds: `curl http://127.0.0.1:<PORT>/healthz` → 200 OK
- [ ] Service responds: `curl http://127.0.0.1:<PORT>/v1/meta` → 200 OK
- [ ] Port binding is localhost-only: `127.0.0.1:<PORT>:<PORT>`
- [ ] No nginx containers in docker-compose.yml (production)
- [ ] Environment variables documented in `.env.example`
- [ ] No secrets in git repository

### Deploy Service
```bash
# On VPS
cd /opt/projects/<service-name>
git pull origin main
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify
curl http://127.0.0.1:<PORT>/healthz
# Expected: 200 OK
```

### Request Nginx Config
**ONLY AFTER** service works on localhost:
1. Create GitHub issue with `infrastructure` label
2. Provide: service name, domain, port
3. Infrastructure team will deploy nginx configuration
4. Wait for confirmation before testing HTTPS

### Verify HTTPS (After Nginx Config)
```bash
# Health check
curl https://<domain>/healthz
# Expected: 200 OK

# Security headers
curl -I https://<domain>/healthz | grep -i "x-frame-options"
# Expected: X-Frame-Options: DENY
```

---

## ❌ Forbidden Actions

**NEVER:**
- ❌ Run nginx in Docker container (production)
- ❌ Bind to `0.0.0.0:80` or `0.0.0.0:443`
- ❌ Edit system nginx configuration files
- ❌ Restart or reload nginx
- ❌ Modify other projects' nginx configs
- ❌ Deploy without health checks
- ❌ Commit secrets to git
- ❌ Assume ports or domains without coordination

---

## 🛑 When to STOP and Escalate

**STOP immediately if:**
- ✋ Health check fails: `curl http://127.0.0.1:<PORT>/healthz` not 200 OK
- ✋ Nginx is not running: `sudo systemctl status nginx` not active
- ✋ Port conflict: Another service using your port
- ✋ ANY checklist item is NO
- ✋ Uncertain about nginx, ports, or domains
- ✋ Potential impact on other services

**Then:**
1. ❌ DO NOT PROCEED with deployment
2. 📝 Document your intent in a proposal
3. 🚨 Create GitHub issue with `infrastructure` label
4. ⏸️ Wait for infrastructure team review

---

## 🔍 Quick Troubleshooting

### Service won't start
```bash
# Check logs
docker compose logs

# Check environment
docker compose config

# Verify .env.prod
cat .env.prod
```

### Health check fails
```bash
# Check container
docker compose ps

# Check port binding
docker compose config | grep ports

# Test inside container
docker compose exec app curl localhost:8000/healthz
```

### 502 Bad Gateway
```bash
# Check service
curl http://127.0.0.1:<PORT>/healthz

# Check nginx logs (infrastructure team)
sudo tail -f /var/log/nginx/error.log
```

### Missing security headers
- Infrastructure team will verify nginx configuration
- Template: `nginx/templates/client_system_nginx.conf.template`

---

## 📁 Required Files Checklist

- [ ] `README.md` — Service description, setup instructions
- [ ] `.env.example` — All environment variables (no secrets)
- [ ] `docker-compose.yml` — Development configuration
- [ ] `docker-compose.prod.yml` — Production overrides
- [ ] `Dockerfile` — Container build definition
- [ ] `.dockerignore` — Build context exclusions
- [ ] `.gitignore` — Git exclusions (must include `.env`)

**Documentation (recommended):**
- [ ] `docs/PROJECT_CONTRACT.md` — Integration contract
- [ ] `docs/DEPLOYMENT.md` — Deployment guide
- [ ] `docs/GUARDRAILS.md` — Development guidelines

---

## 🎯 Success Criteria

Deployment is successful when:
- ✅ `curl http://127.0.0.1:<PORT>/healthz` → 200 OK
- ✅ `curl https://<domain>/healthz` → 200 OK
- ✅ Security headers present in HTTPS response
- ✅ No nginx containers: `docker ps --filter "ancestor=nginx"` → empty
- ✅ System nginx owns 80/443: `sudo netstat -tlnp | grep ':80\|:443'` → nginx only
- ✅ No other services affected
- ✅ Can rollback: `docker compose down` works cleanly

---

## 📚 Full Documentation

For detailed information, see:
- **[PROJECT_CONTRACT.md](./PROJECT_CONTRACT.md)** — Complete API and integration contract
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** — Detailed deployment guide with troubleshooting
- **[ADR_SYSTEM_NGINX.md](./ADR_SYSTEM_NGINX.md)** — Architectural rationale
- **[AGENT_NEW_PROJECT_CHECKLIST.md](./AGENT_NEW_PROJECT_CHECKLIST.md)** — Comprehensive checklist
- **[CODEX_AGENT_BEHAVIOR_LOCK.md](./CODEX_AGENT_BEHAVIOR_LOCK.md)** — Agent behavior rules
- **[CLIENT_PROJECT_TEMPLATE.md](./CLIENT_PROJECT_TEMPLATE.md)** — Template for new projects

---

## 🆘 Getting Help

1. **Check documentation** (links above)
2. **Create GitHub issue** with `infrastructure` label
3. **Include in issue:**
   - Service name, domain, port
   - What you tried
   - Expected vs actual behavior
   - Relevant logs
4. **Wait for response** before proceeding

---

**Remember:** 
> **"If unsure → document. If risky → stop. If infra → never guess."**

---

**Version:** 1.0  
**Last Updated:** 2025-12-26  
**Status:** Active
