# ADR: System Nginx as the Sole Reverse Proxy for Multi-Project VPS

## Status

**Accepted**

## Context

FlowBiz operates a single VPS hosting multiple client projects and services. Each service runs in Docker containers and must be accessible via HTTPS on standard ports (80/443). The infrastructure must support:

- **Multiple client projects** running simultaneously on the same host
- **Shared ports 80/443** for all public HTTP/HTTPS traffic
- **Client services** running on host-published localhost ports (e.g., 127.0.0.1:3001, 127.0.0.1:3002)
- **TLS termination** with Let's Encrypt certificate management
- **Domain routing** to appropriate backend services based on subdomain or path
- **Operational simplicity** for agents deploying new projects

## Decision

**FlowBiz uses System Nginx (managed via systemd) as the only reverse proxy for all production services.**

All client projects MUST:
- Bind their services to localhost-only ports (127.0.0.1:<PORT>)
- Route public traffic through system nginx configurations in `/etc/nginx/conf.d/`
- NOT run nginx containers in their docker-compose stacks

## Rationale

### 1. Docker Bridge Network Isolation
Docker containers running on the same host use bridge networking by default. When a service binds to `0.0.0.0:80` inside a container, Docker cannot share that port with other containers. This creates port conflicts when multiple projects need public HTTP/HTTPS access.

**System nginx solution:** Nginx runs outside Docker on the host, owns ports 80/443 once, and routes to all services via localhost ports.

### 2. Host Port Accessibility
Services bound to `127.0.0.1:<PORT>` via Docker's port mapping (e.g., `ports: ["127.0.0.1:3001:3001"]`) are accessible from the host but isolated from external networks. System nginx proxies requests from public interfaces to these internal ports.

**This architecture provides:**
- Network isolation (services not directly exposed)
- Centralized routing (one place to configure all domains)
- Port sharing (all projects use 80/443 via nginx)

### 3. TLS Certificate Management
Let's Encrypt certificates must be issued on the host system, not inside ephemeral containers. System nginx provides stable paths for certificates (`/etc/letsencrypt/live/<domain>/`) and integrates directly with certbot for automated renewal.

**Docker nginx problems:**
- Certificates inside containers require volume mounts or rebuilds
- Certbot running in containers complicates renewal automation
- Certificate renewal requires nginx reload, which is simpler with systemd

### 4. Operational Simplicity
System nginx provides a stable, predictable deployment model:
- **One configuration location:** All routing lives in `/etc/nginx/conf.d/*.conf`
- **One reload command:** `sudo systemctl reload nginx` applies all changes
- **One service to monitor:** `sudo systemctl status nginx`
- **Declarative routing:** Each client gets one config file with clear upstream targets

**Docker nginx drawbacks:**
- Multiple nginx containers create confusion (which container routes which domain?)
- Requires Docker network inspection to determine routing
- Log aggregation becomes fragmented across containers
- Restart impacts are harder to predict with multiple nginx instances

## Consequences

### What This Means

**Mandatory:**
- System nginx is the only reverse proxy in production
- All client services bind to `127.0.0.1:<PORT>` in docker-compose
- All domain routing lives in `/etc/nginx/conf.d/<domain>.conf`
- One domain/subdomain = one clear nginx config file

**Forbidden:**
- Running nginx containers in docker-compose (production)
- Binding services to `0.0.0.0:80` or `0.0.0.0:443`
- Creating docker-to-docker proxy chains (nginx → nginx)
- Editing shared nginx config files for multiple domains

**Operational workflow:**
1. Deploy client service with localhost-only port binding
2. Create nginx config file: `/etc/nginx/conf.d/<domain>.conf`
3. Test config: `sudo nginx -t`
4. Reload nginx: `sudo systemctl reload nginx`
5. Verify health: `curl -k https://<domain>/healthz`

### What We Gain

- **Stability:** One nginx instance, one source of truth for routing
- **Predictability:** All agents follow the same deployment pattern
- **Observability:** Centralized nginx logs at `/var/log/nginx/`
- **Security:** Services isolated behind localhost-only bindings
- **Maintainability:** Clear separation between service deployment and routing configuration

### What We Lose

- **Docker Compose self-sufficiency:** Services cannot "just work" with `docker-compose up` in production (by design, for safety)
- **Container-level TLS:** TLS termination happens at system nginx, not in containers (this is intentional)

## Alternatives Considered

### Docker Nginx in Containers (Rejected)

**Why rejected:**
- Port 80/443 conflicts across multiple projects
- TLS certificate management complexity (volumes, renewal, container restarts)
- Routing becomes opaque (requires Docker network inspection)
- Multiple nginx instances create operational overhead

**When it's acceptable:**
- Local development environments (`docker-compose.yml` for dev)
- Single-project deployments (not applicable here)

### Traefik or Caddy as System Reverse Proxy (Rejected)

**Why rejected:**
- Increases complexity (learning curve, configuration paradigms)
- Nginx is the established standard with proven operational knowledge
- Traefik/Caddy provide auto-discovery benefits primarily for dynamic container orchestration (Kubernetes, Swarm), which we do not use
- Migration cost outweighs marginal benefits

**When reconsidered:**
- If infrastructure shifts to container orchestration (Kubernetes, Nomad)
- If auto-discovery and dynamic routing become hard requirements

## Compliance

All new client projects MUST adhere to this decision. Agents deploying services that violate this architecture MUST NOT proceed with deployment and MUST escalate via documentation PR or GitHub issue.

**Verification command:**
```bash
# No nginx containers should exist
docker ps --filter "name=nginx" --filter "ancestor=nginx"
# Expected: No results

# System nginx should own ports 80/443
sudo netstat -tlnp | grep ':80\|:443'
# Expected: nginx process
```

## References

- **Implementation guide:** `docs/AGENT_NEW_PROJECT_CHECKLIST.md`
- **Template config:** `nginx/templates/client_system_nginx.conf.template`
- **Existing documentation:** `docs/CODEX_SYSTEM_NGINX_FIRST.md`

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-25  
**Status:** Accepted (Non-negotiable)
