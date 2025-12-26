# Agent Pre-Flight Checklist — New Client Project Deployment

## Purpose

This checklist is **MANDATORY** for all agents deploying new client projects to the FlowBiz VPS. Every item must be verified before proceeding. If any checkbox is **NO**, deployment is **forbidden**.

---

## ✅ Before Deploy (Hard Stop)

### Service Validation

- [ ] **Client service port confirmed and documented**  
  Example: Service runs on port 3001, binds to `127.0.0.1:3001`

- [ ] **Health endpoint responds on localhost**  
  Test: `curl http://127.0.0.1:<PORT>/healthz` returns `200 OK`

- [ ] **Metadata endpoint responds on localhost**  
  Test: `curl http://127.0.0.1:<PORT>/v1/meta` returns version info

- [ ] **Service has unique port (no conflicts)**  
  Ports 80, 443, 8000, 5432 are reserved. Use 3001+, 8001+, etc.

### Docker Compose Configuration

- [ ] **No nginx service in docker-compose.yml (production)**  
  Verify: No service named `nginx` in production compose files

- [ ] **Service binds to localhost only**  
  Verify: Port mapping uses `127.0.0.1:<PORT>:<PORT>`, NOT `0.0.0.0:<PORT>:<PORT>`

- [ ] **Environment file configured**  
  `.env` or `.env.prod` exists with all required variables

- [ ] **No ports 80/443 exposed in docker-compose**  
  Verify: No `ports: ["80:80"]` or `ports: ["443:443"]` entries

### Security

- [ ] **No secrets committed to git**  
  `.env` files in `.gitignore`, no API keys in code

- [ ] **Environment file permissions set**  
  `chmod 600 .env.prod` applied

- [ ] **Strong database password configured**  
  If using database, password is not default/weak

---

## ✅ Nginx Rules (System Nginx Only)

### Configuration Standards

- [ ] **System nginx is the only reverse proxy**  
  Verify: `docker ps | grep nginx` returns no results in production

- [ ] **One domain = one nginx config file**  
  Template: `/etc/nginx/conf.d/<domain>.conf`

- [ ] **Config file uses localhost upstream**  
  `proxy_pass http://127.0.0.1:<PORT>;` (NOT Docker service name)

- [ ] **No wildcard edits to shared configs**  
  Do NOT modify other projects' config files in `/etc/nginx/conf.d/`

- [ ] **HTTP → HTTPS redirect configured**  
  Port 80 server block redirects to HTTPS

- [ ] **Security headers present**  
  Config includes: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, HSTS

- [ ] **TLS certificate paths prepared**  
  Placeholders for `/etc/letsencrypt/live/<domain>/fullchain.pem`

### Testing

- [ ] **Nginx config syntax validated**  
  Test: `sudo nginx -t` returns "syntax is ok"

- [ ] **Nginx service is running**  
  Test: `sudo systemctl status nginx` shows "active (running)"

---

## ❌ Forbidden Actions

You **MUST NOT** do any of the following:

- [ ] **✅ VERIFIED: Will NOT restart nginx without testing first**  
  Always run `sudo nginx -t` before `sudo systemctl reload nginx`

- [ ] **✅ VERIFIED: Will NOT touch other project configs**  
  Only create/modify config for this project's domain

- [ ] **✅ VERIFIED: Will NOT run nginx in docker-compose**  
  No nginx container in production stack

- [ ] **✅ VERIFIED: Will NOT bind to 0.0.0.0:80 or 0.0.0.0:443**  
  Service ports bind to 127.0.0.1 only

- [ ] **✅ VERIFIED: Will NOT deploy without health checks**  
  `/healthz` and `/v1/meta` endpoints exist

- [ ] **✅ VERIFIED: Will NOT modify core infrastructure**  
  No changes to `/opt/flowbiz/flowbiz-ai-core/`

---

## 🚀 Deployment Verification

### After Deployment (Post-Deploy Checks)

- [ ] **Service container is running**  
  Test: `docker compose ps` shows service as "Up"

- [ ] **Health check succeeds (localhost)**  
  Test: `curl http://127.0.0.1:<PORT>/healthz` returns `200 OK`

- [ ] **Nginx config loaded without errors**  
  Test: `sudo nginx -t && sudo systemctl reload nginx` succeeds

- [ ] **Domain resolves via HTTPS**  
  Test: `curl -k https://<domain>/healthz` returns `200 OK`

- [ ] **Security headers present in response**  
  Test: `curl -I https://<domain>/healthz | grep -i "x-frame-options"`

- [ ] **No 502 or connection refused errors**  
  Test: Public endpoint returns expected HTTP 200, not 502/504

---

## 📋 Escalation Rule

### When to Stop and Escalate

**If ANY of these conditions are true:**

1. **Any checkbox above is NO**
2. **Uncertain about nginx configuration**
3. **Port conflicts detected**
4. **Health checks fail after deployment**
5. **TLS certificate issues**
6. **Other projects' services affected**

**Then you MUST:**

- ❌ **DO NOT PROCEED** with deployment
- ✅ **STOP** all changes immediately
- ✅ **ESCALATE** by creating a doc-only PR proposing your approach
- ✅ **DOCUMENT** the issue and open a GitHub issue for guidance
- ✅ **ROLLBACK** any partial changes if safe to do so

### Escalation Contacts

- **Documentation questions:** Open PR to `docs/` with questions in description
- **Infrastructure issues:** Create GitHub issue with `infrastructure` label
- **Urgent production issues:** Contact core team immediately

---

## 🧠 Mental Model

**This checklist exists to prevent infrastructure incidents.**

Every item represents a past mistake or near-miss. If you skip items or check boxes without verification, you risk:

- Breaking existing client services
- Causing downtime for production domains
- Creating security vulnerabilities
- Making the VPS unstable or unrecoverable

**When in doubt, stop. Ask first. Deploy later.**

---

## 🔄 Rollback Preparation

Before deploying, ensure you can rollback:

- [ ] **Previous git commit SHA documented**  
  Can revert via `git checkout <sha>`

- [ ] **Backup of existing nginx config (if modifying)**  
  Copy existing config before changes

- [ ] **Service can be stopped cleanly**  
  `docker compose down` does not affect other services

- [ ] **Rollback steps documented**  
  Written plan for reverting this deployment

---

## 🚫 Exit Criteria for NO-GO Decision

**Deployment is FORBIDDEN if:**

- Health endpoint does not return 200 OK on localhost
- Nginx service is not running or nginx -t fails
- Port conflicts exist with other services
- TLS certificate paths are invalid or missing
- Any security checklist item is NO
- Any forbidden action cannot be confirmed as avoided

**If any exit criteria is met: STOP. DO NOT DEPLOY.**

---

## ✅ Sign-Off (Virtual Acknowledgment)

By proceeding with deployment after completing this checklist, you acknowledge:

- All checkboxes are ✅ YES
- All forbidden actions are ✅ VERIFIED as avoided
- Escalation rules are understood
- Rollback plan is prepared
- You accept responsibility for this deployment

**If you cannot sign off on all items, create a docs-only PR instead.**

---

## 📚 Related Documentation

- **[ADR_SYSTEM_NGINX.md](./ADR_SYSTEM_NGINX.md)** — Architecture decision for system nginx
- **[CODEX_SYSTEM_NGINX_FIRST.md](./CODEX_SYSTEM_NGINX_FIRST.md)** — System nginx operational guide
- **[CODEX_AGENT_BEHAVIOR_LOCK.md](./CODEX_AGENT_BEHAVIOR_LOCK.md)** — Agent behavior rules and safety locks

---

**Checklist Version:** 1.0  
**Last Updated:** 2025-12-25  
**Maintained by:** FlowBiz Infrastructure Team  

**Remember:** If any checkbox is **NO** → deployment is **forbidden**.
