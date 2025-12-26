# VPS Deployment Guide — System Nginx Architecture

This guide provides step-by-step instructions for deploying FlowBiz AI Core to a Virtual Private Server (VPS) using **System Nginx** (via systemd) as the reverse proxy and Docker Compose for application services.

---

## ⚠️ CRITICAL: Architecture Requirements

**READ FIRST:** [ADR_SYSTEM_NGINX.md](ADR_SYSTEM_NGINX.md)

This deployment **REQUIRES**:
- ✅ System nginx via systemd as the ONLY reverse proxy
- ✅ Services bind to localhost ports only (127.0.0.1:<PORT>)
- ✅ All routing configs in `/etc/nginx/conf.d/`
- ❌ NO Docker nginx containers in production
- ❌ NO services binding to 0.0.0.0:80 or 0.0.0.0:443

**If you violate these rules, your deployment will be rejected.**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Install Dependencies](#install-dependencies)
4. [Install System Nginx](#install-system-nginx)
5. [Clone Repository](#clone-repository)
6. [Configure Environment](#configure-environment)
7. [Deploy Application Services](#deploy-application-services)
8. [Configure System Nginx](#configure-system-nginx)
9. [SSL/TLS Setup](#ssltls-setup)
10. [Verify Deployment](#verify-deployment)
11. [Maintenance](#maintenance)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### VPS Requirements

- **Operating System**: Ubuntu 22.04 LTS (or similar Linux distribution)
- **RAM**: Minimum 2GB (4GB recommended)
- **CPU**: 2 cores minimum
- **Storage**: 20GB minimum
- **Network**: Public IP address with open ports 80 and 443

### Local Requirements

- SSH client for server access
- Git (optional, for cloning)
- Basic knowledge of Linux command line

### Domain Setup (Required for Production)

- Domain name pointing to your VPS IP address
- DNS A record configured (e.g., `flowbiz.cloud` → VPS IP)
- Subdomain records for client services (e.g., `client1.flowbiz.cloud` → VPS IP)

---

## Server Setup

### 1. Connect to Your VPS

```bash
ssh root@YOUR_VPS_IP
```

Replace `YOUR_VPS_IP` with your server's IP address.

### 2. Update System Packages

```bash
apt update && apt upgrade -y
```

### 3. Create Non-Root User (Recommended)

```bash
# Create user
adduser flowbiz

# Add to sudo group
usermod -aG sudo flowbiz

# Switch to new user
su - flowbiz
```

### 4. Configure Firewall

```bash
# Allow SSH
sudo ufw allow OpenSSH

# Allow HTTP (for Let's Encrypt challenge and HTTP→HTTPS redirect)
sudo ufw allow 80/tcp

# Allow HTTPS (for production traffic)
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

**Important:** Ports 80 and 443 will be owned by system nginx. No Docker containers should bind to these ports.

---

## Install Dependencies

### 1. Install Docker

```bash
# Install required packages
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index
sudo apt update

# Install Docker
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Verify installation
docker --version
```

### 2. Install Docker Compose

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### 3. Add User to Docker Group

```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Apply group membership (log out and back in, or use newgrp)
newgrp docker

# Verify Docker access without sudo
docker ps
```

### 4. Install Git

```bash
sudo apt install -y git
```

---

## Install System Nginx

**CRITICAL:** Install nginx on the host system, NOT in Docker.

### 1. Install Nginx

```bash
# Install nginx
sudo apt install -y nginx

# Verify installation
nginx -v
```

### 2. Start and Enable Nginx

```bash
# Start nginx service
sudo systemctl start nginx

# Enable nginx to start on boot
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

**Expected:** Nginx should be `active (running)`.

### 3. Verify Nginx Owns Ports 80/443

```bash
# Check which process is listening on ports 80 and 443
sudo netstat -tlnp | grep -E ':(80|443)'
```

**Expected output:**
```
tcp  0  0 0.0.0.0:80  0.0.0.0:*  LISTEN  <PID>/nginx: master process
```

### 4. Create Nginx Configuration Directory

```bash
# Nginx configs will be stored in /etc/nginx/conf.d/
# This directory typically exists by default
sudo ls -la /etc/nginx/conf.d/
```

### 5. Remove Default Nginx Site (Optional)

```bash
# Remove default site to avoid conflicts
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

---

## Clone Repository

### Create Project Directory

```bash
# Create deployment directory
sudo mkdir -p /opt/flowbiz

# Change ownership to your user
sudo chown -R $USER:$USER /opt/flowbiz

# Navigate to directory
cd /opt/flowbiz
```

### Option 1: Clone via Git (Recommended)

```bash
# Clone repository
git clone https://github.com/natbkgift/flowbiz-ai-core.git

# Navigate to project directory
cd flowbiz-ai-core
```

### Option 2: Upload via SCP

From your local machine:

```bash
# Compress repository
tar -czf flowbiz-ai-core.tar.gz flowbiz-ai-core/

# Upload to VPS
scp flowbiz-ai-core.tar.gz flowbiz@YOUR_VPS_IP:/opt/flowbiz/

# On VPS, extract
cd /opt/flowbiz
tar -xzf flowbiz-ai-core.tar.gz
cd flowbiz-ai-core
```

---

## Configure Environment

### 1. Create Environment File

```bash
# Copy example environment file
cp .env.example .env

# Edit environment file
nano .env
```

### 2. Update Environment Variables

Update the following variables in `.env`:

```bash
# Application Configuration
APP_ENV=production
APP_NAME=FlowBiz AI Core
FLOWBIZ_VERSION=0.1.0
APP_LOG_LEVEL=INFO

# Set GIT_SHA to current commit (optional - use shell command to get value)
# Example: FLOWBIZ_GIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
FLOWBIZ_GIT_SHA=unknown
# Optional build metadata
# FLOWBIZ_BUILD_TIME=2024-01-01T00:00:00Z
# Legacy APP_VERSION/GIT_SHA/BUILD_TIME remain supported for backward compatibility but are deprecated.

# Database Configuration (change password!)
POSTGRES_USER=flowbiz
POSTGRES_PASSWORD=CHANGE_THIS_SECURE_PASSWORD
POSTGRES_DB=flowbiz
APP_DATABASE_URL=postgresql://flowbiz:CHANGE_THIS_SECURE_PASSWORD@db:5432/flowbiz

# CORS Configuration (adjust for your domain)
APP_CORS_ALLOW_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
APP_CORS_ALLOW_METHODS=GET,POST,PUT,PATCH,DELETE
APP_CORS_ALLOW_HEADERS=Content-Type,Authorization
APP_CORS_ALLOW_CREDENTIALS=false

# API Configuration
APP_API_HOST=0.0.0.0
APP_API_PORT=8000
```

**Important Security Notes:**
- Change `POSTGRES_PASSWORD` to a strong, unique password
- Update `APP_CORS_ALLOW_ORIGINS` with your actual domain(s)
- Never commit `.env` to version control

### 3. Secure Environment File

```bash
# Set restrictive permissions
chmod 600 .env

# Verify permissions
ls -la .env
```

---

## Deploy Application Services

**IMPORTANT:** We deploy **only** the application services (API + Database). **NO nginx container** in production.

### 1. Create Production Docker Compose Override

Create a production override file if it doesn't exist:

```bash
cd /opt/flowbiz/flowbiz-ai-core
nano docker-compose.prod.yml
```

Add the following content (this removes nginx and binds API to localhost only):

```yaml
version: '3.8'

services:
  api:
    restart: always
    ports:
      - "127.0.0.1:8000:8000"  # Bind to localhost only
    environment:
      APP_ENV: production
      APP_LOG_LEVEL: WARNING
    command: uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --workers 4

  db:
    restart: always
    ports:
      - "127.0.0.1:5432:5432"  # Bind to localhost only
```

**Key Points:**
- API binds to `127.0.0.1:8000` (accessible only from host)
- Database binds to `127.0.0.1:5432` (accessible only from host)
- No nginx service (system nginx will handle routing)

### 2. Build and Start Services

```bash
# Build and start services with production override
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

This command will:
- Build the API Docker image
- Pull PostgreSQL image
- Create necessary volumes
- Start API and database services (NO nginx)

### 3. Monitor Startup

```bash
# View logs from all services
docker-compose logs -f

# View logs from specific service
docker-compose logs -f api
docker-compose logs -f db
```

Press `Ctrl+C` to stop following logs.

### 4. Check Service Status

```bash
# List running containers
docker-compose ps

# Expected output (NO nginx container):
# NAME                COMMAND                  SERVICE   STATUS          PORTS
# flowbiz-api         "uvicorn apps.api.ma…"   api       Up 2 minutes    127.0.0.1:8000->8000/tcp
# flowbiz-db          "docker-entrypoint.s…"   db        Up 2 minutes    127.0.0.1:5432->5432/tcp
```

**Verify NO nginx container exists:**
```bash
docker ps | grep nginx
```
**Expected:** No output (no nginx container should be running).

### 5. Test API on Localhost

```bash
# Test API directly on localhost (from VPS)
curl http://127.0.0.1:8000/healthz

# Expected response:
# {"status":"ok","service":"FlowBiz AI Core","version":"0.1.0"}
```

**Important:** At this point, the API is accessible only from the VPS itself (not publicly). System nginx will proxy public traffic to it.

---

## Configure System Nginx

Now that the application services are running on localhost, configure system nginx to proxy public traffic to them.

### 1. Copy Nginx Template

```bash
# Copy the client template for system nginx
sudo cp /opt/flowbiz/flowbiz-ai-core/nginx/templates/client_system_nginx.conf.template \
     /etc/nginx/conf.d/flowbiz.cloud.conf

# Edit the file
sudo nano /etc/nginx/conf.d/flowbiz.cloud.conf
```

### 2. Update Placeholders

Replace the following placeholders in the file:
- `{{DOMAIN}}` → `flowbiz.cloud` (your actual domain)
- `{{PORT}}` → `8000` (the localhost port where API is running)

You can use sed to automate this:

```bash
sudo sed -i 's/{{DOMAIN}}/flowbiz.cloud/g' /etc/nginx/conf.d/flowbiz.cloud.conf
sudo sed -i 's/{{PORT}}/8000/g' /etc/nginx/conf.d/flowbiz.cloud.conf
```

### 3. Verify Nginx Configuration

```bash
# Test nginx configuration syntax
sudo nginx -t

# Expected output:
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 4. Reload Nginx

```bash
# Reload nginx to apply the new configuration
sudo systemctl reload nginx

# Check status
sudo systemctl status nginx
```

**Important:** At this stage, nginx will try to use SSL certificates that don't exist yet. The HTTPS server block will fail, but HTTP should work.

### 5. Test HTTP Access (Temporary)

```bash
# Test from VPS localhost
curl http://localhost/healthz

# Test from external client (if HTTP is working)
curl http://YOUR_VPS_IP/healthz
```

**Next Step:** Obtain SSL certificates to enable HTTPS.

---

## SSL/TLS Setup

**CRITICAL:** SSL certificates are managed by Certbot on the host system, NOT in Docker containers.

### 1. Install Certbot

```bash
# Install certbot with nginx plugin
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Obtain SSL Certificate

Before running certbot, temporarily comment out the HTTPS server block in the nginx config since we don't have certificates yet:

```bash
# Edit the nginx config
sudo nano /etc/nginx/conf.d/flowbiz.cloud.conf
```

Comment out the entire HTTPS server block (lines starting with `server {` for port 443) by adding `#` at the beginning of each line, OR remove it temporarily.

**OR** use certbot with standalone mode (recommended for first-time setup):

```bash
# Stop nginx temporarily
sudo systemctl stop nginx

# Obtain certificate using standalone mode
sudo certbot certonly --standalone -d flowbiz.cloud -d www.flowbiz.cloud

# Start nginx again
sudo systemctl start nginx
```

Follow the prompts:
- Enter your email address
- Agree to Terms of Service
- Choose whether to share your email

**Certificate Location:**
```
/etc/letsencrypt/live/flowbiz.cloud/fullchain.pem
/etc/letsencrypt/live/flowbiz.cloud/privkey.pem
```

### 3. Uncomment HTTPS Server Block

Now that certificates exist, uncomment or re-add the HTTPS server block in the nginx config:

```bash
sudo nano /etc/nginx/conf.d/flowbiz.cloud.conf
```

Ensure the HTTPS server block (port 443) is present and points to the correct certificate paths.

### 4. Test and Reload Nginx

```bash
# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### 5. Verify HTTPS

```bash
# Test from VPS
curl https://localhost/healthz -k

# Test from external client
curl https://flowbiz.cloud/healthz

# Check security headers
curl -I https://flowbiz.cloud/healthz
```

**Expected Headers:**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`

### 6. Set Up Certificate Auto-Renewal

```bash
# Test renewal process (dry run)
sudo certbot renew --dry-run

# Check certbot timer status (auto-renewal runs twice daily)
sudo systemctl status certbot.timer

# Enable timer if not already enabled
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

**Important:** Certbot automatically renews certificates. After renewal, nginx needs to reload:

```bash
# Test manual renewal
sudo certbot renew

# Reload nginx after certificate renewal
sudo systemctl reload nginx
```

Consider adding a renewal hook to auto-reload nginx:

```bash
# Create renewal hook
sudo nano /etc/letsencrypt/renewal-hooks/post/reload-nginx.sh
```

Add the following content:

```bash
#!/bin/bash
systemctl reload nginx
```

Make it executable:

```bash
sudo chmod +x /etc/letsencrypt/renewal-hooks/post/reload-nginx.sh
```

---

## Verify Deployment

After system nginx is configured with SSL, verify everything works end-to-end.

### 1. Test Health Endpoint

```bash
# From VPS
curl https://localhost/healthz -k

# From external client
curl https://flowbiz.cloud/healthz

# Expected response:
# {"status":"ok","service":"FlowBiz AI Core","version":"0.1.0"}
```

### 2. Test Metadata Endpoint

```bash
curl https://flowbiz.cloud/v1/meta

# Expected response:
# {"service":"FlowBiz AI Core","version":"0.1.0","git_sha":"abc1234","environment":"production"}
```

### 3. Test API Documentation

```bash
# Access Swagger UI in browser
open https://flowbiz.cloud/docs
```

### 4. Verify HTTP → HTTPS Redirect

```bash
curl -I http://flowbiz.cloud/healthz

# Expected: 301 Moved Permanently
# Location: https://flowbiz.cloud/healthz
```

### 5. Verify Security Headers

```bash
curl -I https://flowbiz.cloud/healthz

# Expected headers:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# Referrer-Policy: strict-origin-when-cross-origin
# Permissions-Policy: geolocation=(), microphone=(), camera=()
# Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### 6. Verify Architecture Compliance

Run these checks to confirm system nginx architecture:

```bash
# Verify no nginx containers are running
docker ps | grep nginx
# Expected: No output

# Verify system nginx owns ports 80/443
sudo netstat -tlnp | grep -E ':(80|443)'
# Expected: nginx process, NOT docker-proxy

# Verify API is accessible on localhost only
curl http://127.0.0.1:8000/healthz
# Expected: {"status":"ok",...}

# Verify API is NOT accessible externally on port 8000
curl http://YOUR_VPS_IP:8000/healthz
# Expected: Connection refused (this is correct!)
```

---

## Maintenance

### View Application Logs

```bash
# All services
docker-compose logs -f

# Specific service with timestamp
docker-compose logs -f --timestamps api

# Last 100 lines
docker-compose logs --tail=100 api
```

### View System Nginx Logs

```bash
# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# View logs for specific domain
sudo grep "flowbiz.cloud" /var/log/nginx/access.log | tail -50
```

### Restart Services

```bash
# Restart application services
docker-compose restart

# Restart specific service
docker-compose restart api

# Reload system nginx (for config changes)
sudo systemctl reload nginx

# Restart system nginx (if necessary)
sudo systemctl restart nginx
```

### Stop Services

```bash
# Stop application services (containers remain)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (WARNING: deletes database data)
docker-compose down -v

# System nginx should NOT be stopped (it handles all projects)
# To stop nginx (affects all projects):
# sudo systemctl stop nginx
```

### Update Application

```bash
# Navigate to project directory
cd /opt/flowbiz/flowbiz-ai-core

# Pull latest changes
git pull origin main

# Rebuild and restart application services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

# Verify
curl http://127.0.0.1:8000/healthz
curl https://flowbiz.cloud/healthz
```

### Update System Nginx Configuration

```bash
# Edit nginx config
sudo nano /etc/nginx/conf.d/flowbiz.cloud.conf

# Test configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx

# Verify
curl https://flowbiz.cloud/healthz
```

### Database Backup

```bash
# Backup database
docker-compose exec db pg_dump -U flowbiz flowbiz > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
docker-compose exec -T db psql -U flowbiz flowbiz < backup_20240115_120000.sql
```

### View Container Resource Usage

```bash
# Monitor all containers
docker stats

# Check disk usage
df -h

# Check Docker disk usage
docker system df
```

### Clean Up Unused Resources

```bash
# Remove unused containers, networks, images
docker system prune -a

# Remove unused volumes (WARNING: may delete data)
docker volume prune
```

### SSL Certificate Renewal

```bash
# Test certificate renewal (dry run)
sudo certbot renew --dry-run

# Force renewal if needed (not normally required)
sudo certbot renew --force-renewal

# After renewal, reload nginx
sudo systemctl reload nginx

# Check certificate expiration
sudo certbot certificates
```

---


## Troubleshooting

### Common Issues

#### System Nginx Not Running

**Symptoms:**
- Cannot access website on ports 80/443
- `curl http://YOUR_VPS_IP` fails

**Check nginx status:**
```bash
sudo systemctl status nginx
```

**Fix:**
```bash
# Start nginx
sudo systemctl start nginx

# Enable to start on boot
sudo systemctl enable nginx

# Check for config errors
sudo nginx -t

# View error logs
sudo tail -50 /var/log/nginx/error.log
```

#### Nginx Returns 502 Bad Gateway

**Symptoms:**
- Website loads but returns 502 error
- API not responding

**Possible Causes:**
- API container not running
- API not accessible on localhost:8000
- Nginx config has wrong upstream

**Check API service:**
```bash
# Check if API container is running
docker-compose ps api

# Test API directly on localhost
curl http://127.0.0.1:8000/healthz

# Check API logs
docker-compose logs api
```

**Fix:**
```bash
# Restart API service
docker-compose restart api

# Verify nginx upstream configuration
sudo cat /etc/nginx/conf.d/flowbiz.cloud.conf | grep proxy_pass
# Should show: proxy_pass http://127.0.0.1:8000;
```

#### SSL Certificate Issues

**Symptoms:**
- HTTPS not working
- Browser shows "Your connection is not private"
- Certificate expired warnings

**Check certificates:**
```bash
# List all certificates
sudo certbot certificates

# Check certificate expiration
sudo certbot certificates | grep "Expiry Date"

# Check nginx SSL configuration
sudo cat /etc/nginx/conf.d/flowbiz.cloud.conf | grep ssl_certificate
```

**Fix:**
```bash
# Renew certificates
sudo certbot renew

# Reload nginx
sudo systemctl reload nginx

# Check certbot timer
sudo systemctl status certbot.timer
```

#### Cannot Access API on Port 8000 Externally

**Expected Behavior:** This is CORRECT! The API should NOT be accessible externally on port 8000.

**Verify:**
```bash
# This should work (from VPS)
curl http://127.0.0.1:8000/healthz

# This should fail (from anywhere)
curl http://YOUR_VPS_IP:8000/healthz
# Expected: Connection refused

# Access should only work through nginx on ports 80/443
curl https://flowbiz.cloud/healthz
```

If port 8000 IS accessible externally, check docker-compose port binding:
```bash
# Should bind to 127.0.0.1, NOT 0.0.0.0
docker-compose config | grep -A 2 "ports:"
# Correct: - "127.0.0.1:8000:8000"
# Wrong:   - "8000:8000" or - "0.0.0.0:8000:8000"
```

#### Database Connection Errors

**Symptoms:**
- API logs show "connection refused" or "could not connect to database"
- 500 errors when accessing API endpoints that need database

**Check database:**
```bash
docker-compose ps db

# Should show "healthy" status
```

**Connect to database:**
```bash
docker-compose exec db psql -U flowbiz flowbiz
```

**Check database connection string:**
```bash
# In .env file
cat .env | grep DATABASE_URL
# Should be: postgresql://flowbiz:PASSWORD@db:5432/flowbiz
```

**Reset database (if corrupted):**
```bash
docker-compose down
docker volume rm flowbiz-ai-core_postgres-data
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

#### Nginx Configuration Syntax Errors

**Symptoms:**
- `sudo nginx -t` fails
- Nginx won't reload or restart
- Error logs show configuration errors

**Check configuration:**
```bash
# Test nginx config
sudo nginx -t

# View error details
sudo nginx -t 2>&1 | less

# Check specific config file
sudo cat /etc/nginx/conf.d/flowbiz.cloud.conf
```

**Fix:**
```bash
# Edit configuration
sudo nano /etc/nginx/conf.d/flowbiz.cloud.conf

# Test again
sudo nginx -t

# Reload only if test passes
sudo systemctl reload nginx
```

#### Port Conflicts

**Symptoms:**
- `systemctl start nginx` fails with "address already in use"
- Docker containers fail to start due to port binding errors

**Check what's using ports:**
```bash
# Check ports 80 and 443
sudo netstat -tlnp | grep -E ':(80|443)'

# Check port 8000
sudo netstat -tlnp | grep ':8000'
```

**Fix:**
```bash
# If another process owns ports 80/443 (not nginx):
sudo systemctl stop <other-service>
sudo systemctl start nginx

# If Docker containers conflict on port 8000:
# Ensure only one service uses each localhost port
docker ps -a | grep 8000
```

#### Permission Denied Errors

**Symptoms:**
- Cannot modify files in /opt/flowbiz/
- Docker commands fail
- Cannot access logs

**Fix file permissions:**
```bash
sudo chown -R $USER:$USER /opt/flowbiz/flowbiz-ai-core
```

**Fix Docker permissions:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply changes (log out and back in, or:)
newgrp docker
```

#### High Memory Usage

**Check resource usage:**
```bash
docker stats

# Check disk usage
df -h

# Check Docker disk usage
docker system df
```

**Limit container memory in docker-compose.prod.yml:**
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 512M
```

#### View Container Shell

**Access API container:**
```bash
docker-compose exec api bash
```

**Access database container:**
```bash
docker-compose exec db bash
```

### Reset Deployment

**WARNING: This deletes all data**

```bash
# Stop and remove containers + volumes
docker-compose down -v

# Remove images
docker rmi $(docker images -q "flowbiz-ai-core*")

# Start fresh
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

# Verify
curl http://127.0.0.1:8000/healthz
curl https://flowbiz.cloud/healthz
```

---

## Production Checklist

Before going live, ensure:

- [ ] **System nginx installed and running** (`sudo systemctl status nginx`)
- [ ] **No nginx containers in Docker** (`docker ps | grep nginx` returns nothing)
- [ ] **Services bind to localhost only** (check docker-compose.prod.yml ports)
- [ ] **Nginx config in /etc/nginx/conf.d/** (flowbiz.cloud.conf exists and tested)
- [ ] **SSL certificates installed** (`sudo certbot certificates`)
- [ ] **Certificate auto-renewal enabled** (`sudo systemctl status certbot.timer`)
- [ ] Strong database password set in `.env`
- [ ] `.env` file has restrictive permissions (`chmod 600 .env`)
- [ ] Firewall configured (`sudo ufw status` shows 80/443 open)
- [ ] Domain DNS configured correctly (A record points to VPS IP)
- [ ] CORS origins updated for production domain
- [ ] `APP_ENV` set to `production`
- [ ] Log level appropriate (`INFO` or `WARNING`)
- [ ] Database backups scheduled
- [ ] Monitoring and alerting configured
- [ ] System updates applied (`sudo apt update && sudo apt upgrade`)
- [ ] Health check endpoints accessible (`curl https://flowbiz.cloud/healthz`)
- [ ] Security headers present (`curl -I https://flowbiz.cloud/healthz`)
- [ ] HTTP redirects to HTTPS (`curl -I http://flowbiz.cloud`)

---

## Related Documentation

- **[VPS_STATUS.md](VPS_STATUS.md)** — Current VPS state and operational conventions
- **[ADR_SYSTEM_NGINX.md](ADR_SYSTEM_NGINX.md)** — Architecture decision for system nginx (MANDATORY READING)
- **[CODEX_AGENT_BEHAVIOR_LOCK.md](CODEX_AGENT_BEHAVIOR_LOCK.md)** — Agent behavior rules and safety locks
- **[AGENT_NEW_PROJECT_CHECKLIST.md](AGENT_NEW_PROJECT_CHECKLIST.md)** — Pre-deployment checklist for new projects
- **[AGENT_ONBOARDING.md](AGENT_ONBOARDING.md)** — Agent onboarding guide
- **[CLIENT_PROJECT_TEMPLATE.md](CLIENT_PROJECT_TEMPLATE.md)** — Template for client projects

---

**Document Version:** 2.0 (Updated for System Nginx Architecture)  
**Last Major Update:** 2025-12-26  
**Status:** Active (System Nginx Required)
