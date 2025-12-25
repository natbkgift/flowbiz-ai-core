# TikTok Live Upstream Switch — Core Infra Change

**Ticket:** CORE-INFRA-REQ-002  
**Date:** 2025-12-25  
**Author:** System (via Copilot Agent)

---

## Summary

Switch tiktoklive.flowbiz.cloud routing from **FlowBiz AI Core** (`api:8000`) to **TikTok Live Client** (`127.0.0.1:3001`).

**Scope:**
- Nginx template change only
- Disabled Docker nginx service (use system nginx instead)
- No firewall/port changes
- No breaking changes to other domains
- Preserves all security headers, TLS, HTTP→HTTPS redirects

**Architecture Note:**  
System nginx is required to access host port 127.0.0.1:3001. Docker nginx cannot reach host ports due to bridge network isolation.

---

## Changes

### Files Modified
1. **`nginx/templates/tiktoklive.flowbiz.cloud.conf.template`**
   - **Before:** `proxy_pass http://api:8000;`
   - **After:** `proxy_pass http://127.0.0.1:3001;`
   - Security headers inlined (no snippet dependencies)

2. **`docker-compose.yml`**
   - Disabled nginx service (commented out)
   - System nginx used instead for host port access

### What Stays the Same
- SSL certificates (`/etc/letsencrypt/live/tiktoklive.flowbiz.cloud/`)
- Security headers (X-Frame-Options, HSTS, CSP, etc.)
- Proxy timeouts (2s connect, 30s read/send)
- HTTP→HTTPS 301 redirect

---

## Preconditions (CRITICAL)

Before deploying this change, ensure the **TikTok Live Client** is running on the VPS:

```bash
# On VPS: Verify client gateway is up and responding
curl -fsS http://127.0.0.1:3001/healthz
curl -fsS http://127.0.0.1:3001/v1/meta
```

**Expected response:**
```json
{"status":"ok","service":"TikTok Live Client",...}
```

If client is **not running**, nginx will return **502 Bad Gateway** after this change.

---

## Deployment Steps (Manual)

Execute on VPS as the deployment user:

```bash
# 1. Navigate to core infra repo
cd /opt/flowbiz/flowbiz-ai-core

# 2. Pull latest changes
git pull origin main

# 3. Stop Docker nginx (if running)
docker compose stop nginx && docker compose rm -f nginx

# 4. Deploy nginx config to system nginx
sudo cp nginx/templates/tiktoklive.flowbiz.cloud.conf.template \
  /etc/nginx/conf.d/tiktoklive.flowbiz.cloud.conf

# 5. Validate system nginx config syntax
sudo nginx -t

# Expected output:
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful

# 6. Restart system nginx
sudo systemctl restart nginx

# 7. Verify system nginx is running
sudo systemctl status nginx
```

**Note:** System nginx must be used instead of Docker nginx because Docker containers cannot access host ports (127.0.0.1:3001) due to bridge network isolation.

---

## Verification Tests

### 1. Internal Tests (on VPS)

```bash
# Verify client upstream is reachable
curl -i http://127.0.0.1:3001/healthz
curl -i http://127.0.0.1:3001/v1/meta

# Expected: HTTP 200 OK, service="TikTok Live Client"
```

### 2. Public HTTPS Tests (from any machine)

```bash
# Health check
curl --insecure https://tiktoklive.flowbiz.cloud/healthz

# Metadata endpoint
curl --insecure https://tiktoklive.flowbiz.cloud/v1/meta

# Verify security headers
curl -I --insecure https://tiktoklive.flowbiz.cloud/healthz
```

**Success Criteria:**
- HTTP status: `200 OK`
- Response body includes: `"service":"TikTok Live Client"` or similar (NOT "FlowBiz AI Core")
- Security headers present:
  - `Strict-Transport-Security: max-age=63072000`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: no-referrer`

### 3. TLS Verification

```bash
# Check certificate is valid for tiktoklive.flowbiz.cloud
openssl s_client -connect tiktoklive.flowbiz.cloud:443 -servername tiktoklive.flowbiz.cloud < /dev/null 2>/dev/null | openssl x509 -noout -subject -dates

# Expected:
# subject=CN=tiktoklive.flowbiz.cloud
# notAfter=<future date>
```

---

## Rollback Procedure

If client is unavailable or responses are incorrect:

```bash
# On VPS
cd /opt/flowbiz/flowbiz-ai-core

# 1. Revert to previous commit
git checkout <previous-commit-hash>

# 2. Restart nginx
docker compose restart nginx

# 3. Verify rollback worked (should show Core API response)
curl -k https://tiktoklive.flowbiz.cloud/v1/meta
```

**Alternative:** Temporarily edit the template directly:

```bash
# Edit template on VPS
vi /opt/flowbiz/flowbiz-ai-core/nginx/templates/tiktoklive.flowbiz.cloud.conf.template

# Change line:
# proxy_pass http://127.0.0.1:3001;
# Back to:
# proxy_pass http://api:8000;

# Force recreate nginx container
docker compose up -d --force-recreate nginx
```

---

## Known Issues / Limitations

1. **502 Bad Gateway if client is down:**
   - Nginx has short timeout (2s connect, 30s read)
   - If client is not running or slow to start, users see 502
   - **Mitigation:** Ensure client has `restart: unless-stopped` in docker-compose.yml

2. **No load balancing:**
   - This setup routes to a single client instance
   - For HA, consider multiple client instances + upstream block

3. **No dashboard exposure:**
   - Client dashboard (typically port 3002) remains private (SSH port-forward only)
   - Only gateway API (port 3001) is publicly routed

---

## Security Considerations

- No new ports exposed to public internet
- TLS termination remains at nginx (same cert, same cipher suites)
- Client gateway must implement its own request validation/rate limiting
- Security headers are applied by nginx (X-Frame-Options, HSTS, etc.)
- Client receives forwarded headers:
  - `X-Real-IP`
  - `X-Forwarded-For`
  - `X-Forwarded-Proto: https`

---

## Related Documentation

- [VPS Deployment Guide](./DEPLOYMENT_VPS.md)
- [Reusable Workflow](./REUSABLE_DEPLOYMENT.md)
- [TikTok Routing Setup](./TIKTOK_ROUTING_DEPLOYMENT.md)
- [Nginx Template Reference](../nginx/templates/)

---

## Approval & Review

**Reviewed by:** (Manual review required)  
**Approved by:** (Manual approval required)  
**Deployed by:** (VPS operator name)  
**Deployed at:** (UTC timestamp)

---

## Post-Deployment Checklist

- [ ] `curl -k https://tiktoklive.flowbiz.cloud/healthz` returns 200 OK
- [ ] Response body shows client identity (not core)
- [ ] `curl -k https://tiktoklive.flowbiz.cloud/v1/meta` returns 200 OK
- [ ] Security headers present in response
- [ ] No 502/504 errors in nginx logs
- [ ] Client container is healthy: `docker compose ps` (in client repo)
- [ ] Update monitoring/alerts if applicable

---

**End of Document**
