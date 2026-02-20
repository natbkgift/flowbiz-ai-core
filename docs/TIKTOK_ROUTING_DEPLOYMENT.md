# CORE-INFRA-REQ-001: TikTok Client Routing Implementation

## Overview
This document describes the implementation of production routing for the **flowbiz-client-live-tiktok** service on the FlowBiz shared VPS.

## Routing Strategy Implemented

### Primary: Subdomain Routing (Recommended)
- **Public API:** `https://tiktok.flowbiz.cloud` → `http://127.0.0.1:3001`
- **Dashboard:** Private (no public route) - accessible only via SSH port-forward or VPN

### Rationale
- **Subdomain routing** provides clear service isolation and better scalability
- **Dashboard kept private** (Option A) follows security best practices and avoids unnecessary public exposure
- **Minimal changes** to core infrastructure - only additive nginx configuration

## Files Changed in flowbiz-ai-core

### 1. New Nginx Template
**File:** `nginx/templates/tiktok.flowbiz.cloud.conf.template`
- Subdomain server block for `tiktok.flowbiz.cloud`
- HTTP → HTTPS redirect (port 80 → 443)
- SSL/TLS configuration using certbot certificates
- Security headers from existing snippets
- Proxy configuration for upstream at `127.0.0.1:3001`
- Proxy timeouts: connect=2s, read=30s, send=30s

**Key Features:**
- Includes security headers: X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy, HSTS
- Uses existing proxy_headers.conf snippet for standard proxy settings
- Explicitly defines API routes: `/healthz`, `/v1/meta`, `/v1/analytics/summary`, `/v1/reliability/summary`
- Catch-all location for other API endpoints

## VPS Deployment Commands

### Prerequisites
1. The client service is already deployed at `/opt/flowbiz/clients/flowbiz-client-live-tiktok`
2. Gateway API is running on `127.0.0.1:3001`
3. Dashboard UI is running on `127.0.0.1:3002` (private, no nginx route)
4. **DNS Record:** Add A record for `tiktok.flowbiz.cloud` pointing to VPS IP address
   - Example: `tiktok.flowbiz.cloud. 300 IN A <VPS_IP>`
   - Wait for DNS propagation (usually 5-15 minutes)
   - Verify: `dig tiktok.flowbiz.cloud` or `nslookup tiktok.flowbiz.cloud`

### Step 1: Deploy Updated Nginx Configuration

```bash
# Navigate to core repository
cd /opt/flowbiz/flowbiz-ai-core

# Pull latest changes
git pull origin main

# Verify new template exists
ls -la nginx/templates/tiktok.flowbiz.cloud.conf.template
```

### Step 2: Provision SSL Certificate for Subdomain

```bash
# Run certbot for new subdomain (interactive, will need DNS or HTTP challenge)
sudo certbot certonly --nginx -d tiktok.flowbiz.cloud

# Or if using webroot:
sudo certbot certonly --webroot -w /var/www/certbot -d tiktok.flowbiz.cloud

# Verify certificate was created
sudo ls -la /etc/letsencrypt/live/tiktok.flowbiz.cloud/
```

**Expected output:**
- `fullchain.pem` - Full certificate chain
- `privkey.pem` - Private key

### Step 3: Install System Nginx Vhost + Reload

Templates in this repo are **references**. In production, routing is applied via **system nginx** vhost files in `/etc/nginx/conf.d/`.

```bash
# On VPS
cd /opt/flowbiz/flowbiz-ai-core

# Copy template into system nginx (one domain = one file)
sudo cp nginx/templates/tiktok.flowbiz.cloud.conf.template /etc/nginx/conf.d/tiktok.flowbiz.cloud.conf

# Validate + reload
sudo nginx -t
sudo systemctl reload nginx
```

### Step 6: Verify Routing with Curl

```bash
# Test HTTPS redirect
curl -I http://tiktok.flowbiz.cloud/healthz
# Expected: 301 Moved Permanently → https://tiktok.flowbiz.cloud/healthz

# Test health endpoint
curl -fsS https://tiktok.flowbiz.cloud/healthz
# Expected: {"status":"ok",...} (depends on gateway implementation)

# Test metadata endpoint
curl -fsS https://tiktok.flowbiz.cloud/v1/meta
# Expected: {"service":"...",...}

# Test analytics endpoint (best-effort, may not have data yet)
curl -fsS https://tiktok.flowbiz.cloud/v1/analytics/summary

# Verify security headers
curl -I https://tiktok.flowbiz.cloud/healthz
# Expected headers:
# - X-Content-Type-Options: nosniff
# - X-Frame-Options: DENY
# - Referrer-Policy: strict-origin-when-cross-origin
# - Permissions-Policy: geolocation=(), microphone=(), camera=()
# - Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
```

### Step 7: Test Dashboard (Private Access via SSH)

The dashboard is intentionally NOT exposed publicly. To access it:

```bash
# From local machine, create SSH tunnel to VPS
ssh -L 3002:127.0.0.1:3002 flowbiz-vps

# Then open in browser:
# http://localhost:3002
```

This keeps the dashboard private and secure, accessible only to authorized operators.

## Nginx Configuration Snippets Added

### HTTP Server Block (Port 80)
- Redirects all traffic to HTTPS
- Allows ACME challenges for SSL renewal at `/.well-known/acme-challenge/`

### HTTPS Server Block (Port 443)
- SSL/TLS termination with Let's Encrypt certificates
- TLS 1.2 and 1.3 protocols
- Strong cipher configuration
- HSTS header with 2-year max-age
- Security headers via snippet inclusion
- Proxy pass to `127.0.0.1:3001` with proper headers
- Timeout configuration to prevent infinite hangs

## Security Implementation

### Headers Applied
All responses include:
- `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`

### Proxy Timeouts
- `proxy_connect_timeout: 2s` - Fail fast if upstream unavailable
- `proxy_read_timeout: 30s` - Standard timeout for API responses
- `proxy_send_timeout: 30s` - Standard timeout for request sending

### TLS Configuration
- Protocols: TLSv1.2, TLSv1.3 (no outdated TLS 1.0/1.1)
- Ciphers: HIGH:!aNULL:!MD5 (strong ciphers only)
- Session cache enabled for performance

## Rollback Procedure

If the routing causes issues, follow these steps to rollback:

### Option 1: Remove Nginx Template and Restart

```bash
# Disable the system nginx vhost
sudo mv /etc/nginx/conf.d/tiktok.flowbiz.cloud.conf /etc/nginx/conf.d/tiktok.flowbiz.cloud.conf.disabled

# Validate + reload
sudo nginx -t
sudo systemctl reload nginx

# Verify core services still work
curl https://flowbiz.cloud/healthz
```

### Option 2: Revert Git Commit

```bash
# Navigate to core repository
cd /opt/flowbiz/flowbiz-ai-core

# Find the commit before this change
git log --oneline -5

# Revert to previous commit (replace <commit-sha> with actual SHA)
git checkout <commit-sha>

# Re-deploy containers (if needed)
docker compose up -d --build --remove-orphans

# Ensure system nginx still has the expected vhost
sudo nginx -t
sudo systemctl reload nginx

# Verify
curl https://flowbiz.cloud/healthz
```

### Option 3: Disable SSL Certificate (Temporary)

```bash
# If SSL certificate is causing issues, comment out SSL lines in:
sudo vi /etc/nginx/conf.d/tiktok.flowbiz.cloud.conf

# Then validate + reload
sudo nginx -t
sudo systemctl reload nginx
```

### Post-Rollback Verification

```bash
# Ensure core API still works
curl https://flowbiz.cloud/healthz

# Check nginx is healthy
sudo systemctl status nginx --no-pager

# Review logs for errors
sudo tail -n 80 /var/log/nginx/error.log
```

## Ops Notes

### Changing Upstream Ports

If the client service needs to use different ports in the future:

1. **Locate the system vhost:** `/etc/nginx/conf.d/tiktok.flowbiz.cloud.conf`
2. **Edit proxy_pass directives:**
   - Current: `proxy_pass http://127.0.0.1:3001;`
   - Change to: `proxy_pass http://127.0.0.1:<NEW_PORT>;`
3. **Validate + reload nginx:** `sudo nginx -t && sudo systemctl reload nginx`
4. **Test:** `curl https://tiktok.flowbiz.cloud/healthz`

### Exposing Dashboard Publicly (If Policy Changes)

If future requirements dictate that the dashboard should be public:

1. **Create new vhost file:** `/etc/nginx/conf.d/tiktok-dash.flowbiz.cloud.conf`
2. **Copy structure from the repo template**: `nginx/templates/tiktok.flowbiz.cloud.conf.template`
3. **Change:**
   - `server_name tiktok-dash.flowbiz.cloud;`
   - `proxy_pass http://127.0.0.1:3002;`
   - SSL certificate path: `/etc/letsencrypt/live/tiktok-dash.flowbiz.cloud/...`
   - Consider changing `X-Frame-Options: DENY` to `SAMEORIGIN` if dashboard needs embedding
4. **Provision SSL:** `sudo certbot certonly --nginx -d tiktok-dash.flowbiz.cloud`
5. **Validate + reload nginx:** `sudo nginx -t && sudo systemctl reload nginx`
6. **Update CORS:** Ensure gateway's CORS env includes `https://tiktok-dash.flowbiz.cloud`

### Adding More Client Services

Follow the same pattern:
1. Add a repo template under `nginx/templates/<service-name>.flowbiz.cloud.conf.template` (for review/versioning)
2. Use unique subdomain and upstream port
3. Provision SSL certificate
4. Install/enable the vhost in `/etc/nginx/conf.d/` and reload nginx
5. Test endpoints

### Certificate Renewal

Certbot will automatically renew certificates. The systemd timer runs twice daily:

```bash
# Check renewal timer status
sudo systemctl status certbot.timer

# Test renewal (dry-run)
sudo certbot renew --dry-run

# Force renewal if needed (not recommended unless necessary)
sudo certbot renew --force-renewal
```

## Troubleshooting

### Issue: 502 Bad Gateway

**Possible Causes:**
- Gateway API not running on port 3001
- Gateway API crashed or unhealthy

**Check:**
```bash
# Test gateway directly
curl http://127.0.0.1:3001/healthz

# Check if gateway is listening
sudo netstat -tlnp | grep 3001

# Check client service logs
cd /opt/flowbiz/clients/flowbiz-client-live-tiktok
docker compose logs gateway
```

### Issue: SSL Certificate Error

**Possible Causes:**
- Certificate not provisioned
- Certificate path incorrect
- Certificate expired

**Check:**
```bash
# Verify certificate exists
sudo ls -la /etc/letsencrypt/live/tiktok.flowbiz.cloud/

# Check certificate validity
sudo certbot certificates

# Check nginx error logs
sudo grep -i ssl /var/log/nginx/error.log | tail -n 50
```

### Issue: Connection Timeout

**Possible Causes:**
- Gateway taking too long to respond
- Gateway not responding at all

**Check:**
```bash
# Test with longer timeout
curl --max-time 10 https://tiktok.flowbiz.cloud/healthz

# Check gateway performance
time curl http://127.0.0.1:3001/healthz

# Increase timeouts in nginx template if needed
# proxy_read_timeout 60s;  # Increase from 30s
```

### Issue: CORS Errors (If Dashboard is Exposed Later)

**Solution:**
- Ensure gateway's CORS environment variable includes the dashboard origin
- This is configured in the client service's `.env` file, NOT in nginx
- Example: `CORS_ORIGINS=https://tiktok-dash.flowbiz.cloud`

## Summary

### What Was Implemented
- ✅ Subdomain routing for TikTok API: `https://tiktok.flowbiz.cloud` → `127.0.0.1:3001`
- ✅ Dashboard kept private (Option A recommended) - SSH port-forward only
- ✅ Security headers applied (X-Content-Type-Options, X-Frame-Options, etc.)
- ✅ Proxy timeouts configured (2s connect, 30s read/send)
- ✅ SSL/TLS configuration with Let's Encrypt pattern
- ✅ Minimal, additive changes to core nginx
- ✅ Rollback procedure documented

### What Was NOT Implemented
- ❌ Public dashboard route (kept private as recommended)
- ❌ Path-based routing (subdomain chosen as primary)
- ❌ Rate limiting (use existing core patterns if needed)
- ❌ Custom auth (not required for this task)
- ❌ Firewall changes (not needed)

### Next Steps for VPS Deployment
1. Pull latest changes from `main` branch
2. Provision SSL certificate: `sudo certbot certonly --nginx -d tiktok.flowbiz.cloud`
3. Validate + reload nginx: `sudo nginx -t && sudo systemctl reload nginx`
5. Test: `curl https://tiktok.flowbiz.cloud/healthz`
6. Verify security headers with: `curl -I https://tiktok.flowbiz.cloud/healthz`

---

**Document Version:** 1.0  
**Created:** 2025-12-25  
**Author:** FlowBiz Core Infra Team  
**Related:** CORE-INFRA-REQ-001
