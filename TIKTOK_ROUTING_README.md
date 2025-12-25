# CORE-INFRA-REQ-001: TikTok Client Routing - Quick Reference

## Summary

This PR implements production routing for the **flowbiz-client-live-tiktok** service on the shared FlowBiz VPS.

### Routing Implemented

✅ **Subdomain Routing (Primary)**
- Public API: `https://tiktok.flowbiz.cloud` → `http://127.0.0.1:3001`
- Dashboard: **Private** (no public route, SSH port-forward only)

### Files Changed

| File | Description |
|------|-------------|
| `nginx/templates/tiktok.flowbiz.cloud.conf.template` | Main API subdomain routing config |
| `nginx/templates/tiktok-dash.flowbiz.cloud.conf.template.disabled` | Optional dashboard config (disabled) |
| `docs/TIKTOK_ROUTING_DEPLOYMENT.md` | Comprehensive deployment guide |
| `scripts/deploy_tiktok_routing.sh` | VPS deployment command reference |

## Quick VPS Deployment

```bash
# 1. Pull changes
cd /opt/flowbiz/flowbiz-ai-core
git pull origin main

# 2. Provision SSL certificate
sudo certbot certonly --nginx -d tiktok.flowbiz.cloud

# 3. Test nginx config
docker compose exec nginx nginx -t

# 4. Restart nginx
docker compose restart nginx

# 5. Verify
curl https://tiktok.flowbiz.cloud/healthz
```

## Rollback

```bash
# Disable template and restart
sudo mv nginx/templates/tiktok.flowbiz.cloud.conf.template \
         nginx/templates/tiktok.flowbiz.cloud.conf.template.disabled
docker compose restart nginx
```

## Security Features

✅ TLS/SSL with Let's Encrypt  
✅ HSTS (max-age=63072000, includeSubDomains, preload)  
✅ X-Content-Type-Options: nosniff  
✅ X-Frame-Options: DENY  
✅ Referrer-Policy: strict-origin-when-cross-origin  
✅ Permissions-Policy: geolocation=(), microphone=(), camera=()  
✅ Proxy timeouts: connect=2s, read=30s, send=30s  

## Ops Notes

### Change Upstream Port
Edit `nginx/templates/tiktok.flowbiz.cloud.conf.template`:
```nginx
proxy_pass http://127.0.0.1:<NEW_PORT>;
```
Then restart: `docker compose restart nginx`

### Enable Dashboard (If Needed)
1. Rename: `tiktok-dash.flowbiz.cloud.conf.template.disabled` → `.template`
2. Provision SSL: `sudo certbot certonly --nginx -d tiktok-dash.flowbiz.cloud`
3. Update gateway CORS to include `https://tiktok-dash.flowbiz.cloud`
4. Restart: `docker compose restart nginx`

### Access Private Dashboard
```bash
# From local machine
ssh -L 3002:127.0.0.1:3002 user@vps-host

# Open in browser
http://localhost:3002
```

## Documentation

- **Full Guide:** [docs/TIKTOK_ROUTING_DEPLOYMENT.md](docs/TIKTOK_ROUTING_DEPLOYMENT.md)
- **VPS Status:** [docs/VPS_STATUS.md](docs/VPS_STATUS.md)
- **Agent Onboarding:** [docs/AGENT_ONBOARDING.md](docs/AGENT_ONBOARDING.md)

## Compliance

✅ Follows VPS_STATUS.md conventions  
✅ Follows AGENT_ONBOARDING.md policies  
✅ Minimal, additive changes only  
✅ No core service modifications  
✅ No secrets committed  
✅ No firewall changes  
✅ No new auth systems  
✅ Uses existing security patterns  

---

**Implementation Date:** 2025-12-25  
**PR:** CORE-INFRA-REQ-001-tiktok-routing
