# Infrastructure Documentation — FlowBiz Multi-Project VPS

**Single Source of Truth for Infrastructure Rules & Architecture Decisions**

---

## ⚠️ START HERE: Mandatory Reading

If you are deploying services, making infrastructure changes, or operating on the shared VPS, you **MUST** read these documents in order:

### 1. Architecture Decision (NON-NEGOTIABLE)
**[ADR_SYSTEM_NGINX.md](ADR_SYSTEM_NGINX.md)** — Why system nginx is mandatory and Docker nginx is forbidden.

**Key Points:**
- System nginx via systemd is the ONLY allowed reverse proxy
- Docker-based nginx/Traefik/Caddy are FORBIDDEN in production
- All routing configs MUST live in `/etc/nginx/conf.d/`
- Services MUST bind to localhost only (127.0.0.1:<PORT>)

### 2. Agent Behavior Rules (SAFETY LOCKS)
**[CODEX_AGENT_BEHAVIOR_LOCK.md](CODEX_AGENT_BEHAVIOR_LOCK.md)** — Hard stop rules and forbidden actions.

**Key Points:**
- Never modify VPS configuration directly without checklist
- Never restart nginx without testing first
- Never deploy without completing pre-flight checklist
- If unsure → document first, deploy later

### 3. System Nginx Operations
**[CODEX_SYSTEM_NGINX_FIRST.md](CODEX_SYSTEM_NGINX_FIRST.md)** — Operational guide for system nginx architecture.

**Key Points:**
- Validation checklist before any change
- Health check procedures
- Hotfix playbook
- Definition of done

---

## 📖 Deployment Guides

### For Core Infrastructure Team

**[DEPLOYMENT_VPS.md](DEPLOYMENT_VPS.md)** — Complete step-by-step VPS deployment guide using system nginx.

Covers:
- Server setup and firewall configuration
- Installing Docker + Docker Compose + System Nginx
- Deploying application services (API + Database)
- Configuring system nginx with templates
- SSL/TLS setup with Let's Encrypt
- Verification and troubleshooting

### For New Services/Projects

**[AGENT_NEW_PROJECT_CHECKLIST.md](AGENT_NEW_PROJECT_CHECKLIST.md)** — Mandatory pre-deployment checklist.

**CRITICAL:** Every checkbox must be ✅ YES before deployment is allowed.

**[AGENT_ONBOARDING.md](AGENT_ONBOARDING.md)** — Quick start guide for agents deploying client services.

Covers:
- Allowed vs forbidden actions
- Required endpoints (/healthz, /v1/meta)
- Port allocation guide
- Security checklist
- Rollback procedures
- Escalation rules

**[CLIENT_PROJECT_TEMPLATE.md](CLIENT_PROJECT_TEMPLATE.md)** — Template and requirements for new service projects.

Covers:
- API contract requirements
- Environment variable standards
- Docker configuration patterns
- nginx configuration templates
- Health check implementation

---

## 📊 Current VPS State

**[VPS_STATUS.md](VPS_STATUS.md)** — Live production status and operational conventions.

Provides:
- Current deployed services and their ports
- Infrastructure architecture overview
- System nginx verification commands
- Port allocation table
- Troubleshooting quick reference
- Architecture compliance checklist

---

## 🏗️ Architecture Documents

**[ARCHITECTURE.md](ARCHITECTURE.md)** — System design and technical architecture.

**[GUARDRAILS.md](GUARDRAILS.md)** — Development guardrails and boundaries.

**[TOOLS.md](TOOLS.md)** — Tools and utilities available.

---

## 🚀 Quick Start Workflows

### Deploying a New Client Service

1. **Read mandatory docs:** ADR_SYSTEM_NGINX.md, CODEX_AGENT_BEHAVIOR_LOCK.md
2. **Complete pre-flight:** AGENT_NEW_PROJECT_CHECKLIST.md
3. **Follow template:** CLIENT_PROJECT_TEMPLATE.md
4. **Deploy service:** Bind to `127.0.0.1:<UNIQUE_PORT>` in docker-compose
5. **Configure nginx:** Use `nginx/templates/client_system_nginx.conf.template`
6. **Obtain SSL:** `sudo certbot certonly --nginx -d <your-domain>`
7. **Test and verify:** Follow verification steps in AGENT_ONBOARDING.md

### Adding a New Domain to System Nginx

1. **Copy template:**
   ```bash
   sudo cp /opt/flowbiz/flowbiz-ai-core/nginx/templates/client_system_nginx.conf.template \
        /etc/nginx/conf.d/<domain>.conf
   ```

2. **Replace placeholders:**
   ```bash
   sudo sed -i 's/{{DOMAIN}}/<your-domain>/g' /etc/nginx/conf.d/<domain>.conf
   sudo sed -i 's/{{PORT}}/<your-port>/g' /etc/nginx/conf.d/<domain>.conf
   ```

3. **Obtain SSL certificate:**
   ```bash
   sudo certbot certonly --nginx -d <your-domain>
   ```

4. **Test and reload:**
   ```bash
   sudo nginx -t && sudo systemctl reload nginx
   ```

5. **Verify:**
   ```bash
   curl https://<your-domain>/healthz
   ```

### Troubleshooting Production Issues

1. **Check system nginx:** `sudo systemctl status nginx`
2. **Check nginx logs:** `sudo tail -f /var/log/nginx/error.log`
3. **Check application logs:** `docker-compose logs -f api`
4. **Verify localhost connectivity:** `curl http://127.0.0.1:<PORT>/healthz`
5. **Check port bindings:** `sudo netstat -tlnp | grep -E ':(80|443|<PORT>)'`
6. **Refer to:** DEPLOYMENT_VPS.md#troubleshooting

---

## 🔐 Security & Compliance

### Architecture Compliance Verification

Run these commands to verify system nginx architecture compliance:

```bash
# 1. No nginx containers should exist
docker ps --filter "name=nginx" --filter "ancestor=nginx"
# Expected: No results

# 2. System nginx must own ports 80/443
sudo netstat -tlnp | grep -E ':(80|443)'
# Expected: nginx process (not docker-proxy)

# 3. Services bind to localhost only
docker-compose config | grep -A 2 "ports:"
# Expected: All ports show "127.0.0.1:<PORT>:<PORT>"

# 4. Nginx configs in /etc/nginx/conf.d/
ls -la /etc/nginx/conf.d/*.conf
# Expected: One .conf file per domain

# 5. SSL certificates managed by Certbot
sudo certbot certificates
# Expected: Valid certificates, auto-renewal enabled
```

### Security Checklist

Before deploying to production:

- [ ] System nginx is the only reverse proxy (no Docker nginx)
- [ ] Services bind to localhost only (127.0.0.1:<PORT>)
- [ ] Nginx configs in /etc/nginx/conf.d/ (one domain = one file)
- [ ] SSL certificates obtained and auto-renewal enabled
- [ ] Security headers present in all responses
- [ ] HTTP redirects to HTTPS
- [ ] Strong database passwords (not default)
- [ ] `.env` files not committed to Git
- [ ] Firewall configured (ports 80/443 open only)
- [ ] Health check endpoints respond with 200 OK

---

## 📚 Reference Materials

### Nginx Templates

- **`nginx/templates/client_system_nginx.conf.template`** — Template for new domains
- **`nginx/templates/default.conf.template`** — Default nginx config (if needed)
- **`nginx/snippets/`** — Reusable nginx snippets (deprecated, use full templates)

### Port Allocation Guide

| Port Range | Usage |
|------------|-------|
| 80, 443 | Reserved for system nginx (public) |
| 8000 | Reserved for flowbiz-ai-core API |
| 5432 | Reserved for flowbiz-ai-core database |
| 8001-8099 | Available for client services (internal) |
| 5433-5499 | Available for client databases (internal) |
| 6379-6399 | Available for Redis/cache (internal) |

**Rule:** All ports bind to 127.0.0.1 only. System nginx routes public traffic.

### Environment Variable Conventions

- `APP_*` — Application settings (strict, validated by Pydantic)
- `FLOWBIZ_*` — Metadata and version info (read by core/deployment)
- `POSTGRES_*` — Database configuration
- `<SERVICE>_*` — Service-specific settings (use your service name as prefix)

---

## 🆘 Escalation & Support

### When to STOP and Escalate

STOP immediately and escalate if:

1. **Any checkbox in AGENT_NEW_PROJECT_CHECKLIST.md is NO**
2. **Uncertain about nginx configuration**
3. **Port conflicts detected**
4. **Health checks fail after deployment**
5. **TLS certificate issues affecting core domain**
6. **Other projects' services affected**

### How to Escalate

1. **Document the issue:** Collect error messages, logs, symptoms
2. **Propose doc-only PR:** If it's a documentation gap or unclear requirement
3. **Create GitHub issue:** For bugs, feature requests, or infrastructure questions
4. **Contact core team:** For urgent production issues or downtime

### Safe Fallback

When in doubt:
- ✅ Create a doc-only PR proposing your approach
- ✅ Ask questions via GitHub issues
- ✅ Test changes in local Docker first
- ❌ DO NOT make destructive changes to production
- ❌ DO NOT assume your change won't affect core services

---

## 🎯 Success Criteria

A deployment is considered SUCCESSFUL only if:

- ✅ No existing service is disrupted
- ✅ No infrastructure rules are violated
- ✅ System nginx architecture is maintained
- ✅ All health checks return 200 OK
- ✅ Security headers are present
- ✅ SSL certificates are valid and auto-renewing
- ✅ Services are isolated (localhost binding)
- ✅ Documentation is updated
- ✅ Another agent could reproduce the deployment using the docs

---

## 🔄 Document Maintenance

### Update Frequency

- **VPS_STATUS.md:** Update when services are added/removed or ports change
- **AGENT_NEW_PROJECT_CHECKLIST.md:** Update when new requirements emerge
- **INFRASTRUCTURE_README.md:** Update when major changes occur
- **ADR_SYSTEM_NGINX.md:** Rarely (only if architecture decision changes)

### Document Version History

- **v1.0 (2025-12-24):** Initial infrastructure documentation
- **v2.0 (2025-12-26):** Updated for system nginx architecture (CURRENT)

---

## 📞 Contact

**Maintained by:** FlowBiz Core Team

**Related Repositories:**
- **Core API:** https://github.com/natbkgift/flowbiz-ai-core

**For Infrastructure Issues:**
- Review this documentation first
- Check VPS_STATUS.md for current state
- Follow escalation rules above
- Create GitHub issue with `infrastructure` label

---

**Remember:** If unsure → document first, deploy later. Safety over speed.
