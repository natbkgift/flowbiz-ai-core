#!/bin/bash
# CORE-INFRA-REQ-001: TikTok Client Routing Deployment Script
# This script provides the commands for deploying the TikTok routing on VPS
# 
# USAGE: Review and execute commands manually, do NOT run as a script
# Each command should be verified before proceeding to the next step
#
# Prerequisites:
# - Client service deployed at /opt/flowbiz/clients/flowbiz-client-live-tiktok
# - Gateway API running on 127.0.0.1:3001
# - Dashboard UI running on 127.0.0.1:3002 (private)

echo "================================================================"
echo "STEP 1: Pull latest core repository changes"
echo "================================================================"
cd /opt/flowbiz/flowbiz-ai-core
git pull origin main

echo ""
echo "================================================================"
echo "STEP 2: Verify new nginx template exists"
echo "================================================================"
ls -la nginx/templates/tiktok.flowbiz.cloud.conf.template

echo ""
echo "================================================================"
echo "STEP 3: Provision SSL certificate for subdomain"
echo "================================================================"
echo "Run one of the following commands:"
echo ""
echo "Option A (recommended - nginx plugin):"
echo "  sudo certbot certonly --nginx -d tiktok.flowbiz.cloud"
echo ""
echo "Option B (webroot):"
echo "  sudo certbot certonly --webroot -w /var/www/certbot -d tiktok.flowbiz.cloud"
echo ""
echo "Follow certbot prompts to complete certificate provisioning"

echo ""
echo "================================================================"
echo "STEP 4: Verify certificate was created"
echo "================================================================"
sudo ls -la /etc/letsencrypt/live/tiktok.flowbiz.cloud/
echo "Expected files: fullchain.pem, privkey.pem, cert.pem, chain.pem"

echo ""
echo "================================================================"
echo "STEP 5: Test nginx configuration"
echo "================================================================"
docker compose exec nginx nginx -t
echo "Expected: syntax is ok, test is successful"

echo ""
echo "================================================================"
echo "STEP 6: Restart nginx to load new configuration"
echo "================================================================"
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart nginx

echo ""
echo "================================================================"
echo "STEP 7: Verify nginx is running"
echo "================================================================"
docker compose ps nginx
echo "Expected: State = Up (healthy)"

echo ""
echo "================================================================"
echo "STEP 8: Test routing - HTTP redirect"
echo "================================================================"
curl -I http://tiktok.flowbiz.cloud/healthz
echo "Expected: 301 Moved Permanently"

echo ""
echo "================================================================"
echo "STEP 9: Test routing - HTTPS health check"
echo "================================================================"
curl -fsS https://tiktok.flowbiz.cloud/healthz
echo "Expected: {\"status\":\"ok\",...}"

echo ""
echo "================================================================"
echo "STEP 10: Test routing - Metadata endpoint"
echo "================================================================"
curl -fsS https://tiktok.flowbiz.cloud/v1/meta
echo "Expected: Service metadata JSON"

echo ""
echo "================================================================"
echo "STEP 11: Test routing - Analytics endpoint"
echo "================================================================"
curl -fsS https://tiktok.flowbiz.cloud/v1/analytics/summary
echo "Expected: Analytics data JSON (or error if no data yet)"

echo ""
echo "================================================================"
echo "STEP 12: Test routing - Reliability endpoint"
echo "================================================================"
curl -fsS https://tiktok.flowbiz.cloud/v1/reliability/summary
echo "Expected: Reliability data JSON (or error if no data yet)"

echo ""
echo "================================================================"
echo "STEP 13: Verify security headers"
echo "================================================================"
curl -I https://tiktok.flowbiz.cloud/healthz
echo "Expected headers:"
echo "  - Strict-Transport-Security: max-age=63072000; includeSubDomains; preload"
echo "  - X-Content-Type-Options: nosniff"
echo "  - X-Frame-Options: DENY"
echo "  - Referrer-Policy: strict-origin-when-cross-origin"
echo "  - Permissions-Policy: geolocation=(), microphone=(), camera=()"

echo ""
echo "================================================================"
echo "DEPLOYMENT COMPLETE"
echo "================================================================"
echo "TikTok API is now available at: https://tiktok.flowbiz.cloud"
echo "Dashboard remains private (SSH port-forward): 127.0.0.1:3002"
echo ""
echo "To access dashboard from local machine:"
echo "  ssh -L 3002:127.0.0.1:3002 user@vps-host"
echo "  Then open: http://localhost:3002"
echo ""
echo "================================================================"

echo ""
echo "================================================================"
echo "ROLLBACK PROCEDURE (if needed)"
echo "================================================================"
echo "If deployment causes issues, run:"
echo ""
echo "# Option 1: Disable template"
echo "sudo mv nginx/templates/tiktok.flowbiz.cloud.conf.template \\"
echo "         nginx/templates/tiktok.flowbiz.cloud.conf.template.disabled"
echo "docker compose restart nginx"
echo ""
echo "# Option 2: Revert git commit"
echo "git log --oneline -5  # Find commit SHA"
echo "git revert <commit-sha>"
echo "docker compose restart nginx"
echo ""
echo "# Verify core services"
echo "curl https://flowbiz.cloud/healthz"
echo "================================================================"
