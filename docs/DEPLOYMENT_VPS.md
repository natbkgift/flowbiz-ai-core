# VPS Deployment Guide

This guide provides step-by-step instructions for deploying FlowBiz AI Core to a Virtual Private Server (VPS) using Docker Compose for the application services and system Nginx for the reverse proxy.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Install Dependencies](#install-dependencies)
4. [Clone Repository](#clone-repository)
5. [Configure Environment](#configure-environment)
6. [Deploy with Docker Compose](#deploy-with-docker-compose)
7. [Verify Deployment](#verify-deployment)
8. [SSL/TLS Setup (Optional)](#ssltls-setup-optional)
9. [Maintenance](#maintenance)
10. [Troubleshooting](#troubleshooting)

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

### Domain Setup (Optional but Recommended)

- Domain name pointing to your VPS IP address
- DNS A record configured (e.g., `api.yourdomain.com` → VPS IP)

---

## Server Setup

### 1. Connect to Your VPS

```bash
ssh root@YOUR_VPS_IP
```

If you already have an SSH config alias, you can use the FlowBiz standard alias:

```bash
ssh flowbiz-vps
```

For controlled local deployments over SSH, use the runbook:
- [docs/RUNBOOK_LOCAL_VPS_DEPLOY.md](RUNBOOK_LOCAL_VPS_DEPLOY.md)

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

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS (for future SSL setup)
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

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

### 4. Install Git (Optional)

```bash
sudo apt install -y git
```

---

## Clone Repository

### Option 1: Clone via Git (Recommended)

```bash
# Navigate to home directory
cd ~

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
scp flowbiz-ai-core.tar.gz flowbiz@YOUR_VPS_IP:~

# On VPS, extract
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

## Deploy with Docker Compose

### 1. Build and Start Services

```bash
# Build and start all services in detached mode
docker-compose up --build -d
```

This command will:
- Build the API Docker image
- Pull PostgreSQL image
- Create necessary volumes
- Start the API and database services (api, db)

**Note:** This deployment uses Docker only for the API and database. For production deployments with public access, you must configure system nginx separately as documented in `ADR_SYSTEM_NGINX.md`. The Docker nginx service is intentionally disabled in this configuration.

### 2. Monitor Startup

```bash
# View logs from all services
docker-compose logs -f

# View logs from specific service
docker-compose logs -f api
docker-compose logs -f db
```

Press `Ctrl+C` to stop following logs.

### 3. Check Service Status

```bash
# List running containers
docker-compose ps

# Expected output:
# NAME                COMMAND                  SERVICE   STATUS          PORTS
# flowbiz-api         "uvicorn apps.api.ma…"   api       Up 2 minutes    8000/tcp
# flowbiz-db          "docker-entrypoint.s…"   db        Up 2 minutes    5432/tcp
```

All services should show `Up` status.

---

## Verify Deployment

### 1. Test Health Endpoint (Direct API Access)

```bash
# Test API directly on port 8000
curl http://localhost:8000/healthz

# Expected response:
# {"status":"ok","service":"FlowBiz AI Core","version":"0.1.0"}
```

### 2. Test Metadata Endpoint

```bash
curl http://localhost:8000/v1/meta

# Expected response:
# {"service":"FlowBiz AI Core","version":"0.1.0","git_sha":"abc1234"}
```

### 3. Test Root Endpoint

```bash
curl http://localhost:8000/

# Expected response:
# {"message":"FlowBiz AI Core API"}
```

### 4. Production Access via System Nginx

**Note:** For production deployments with public access, you must configure system nginx as a reverse proxy. This setup is documented in:
- `ADR_SYSTEM_NGINX.md` - Architecture decision and rationale
- `CODEX_SYSTEM_NGINX_FIRST.md` - Operational guide
- `AGENT_NEW_PROJECT_CHECKLIST.md` - Deployment checklist

System nginx configuration should:
- Proxy requests from port 80/443 to the API service on localhost:8000
- Handle TLS termination with Let's Encrypt certificates
- Add security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- Implement Content Security Policy (CSP) for different paths

Example test after system nginx is configured:

```bash
# Test through system nginx (production)
curl http://localhost/healthz

# Or from external client
curl https://api.yourdomain.com/healthz
```

### 5. Check Request ID Header

```bash
curl -i http://localhost:8000/healthz | grep X-Request-ID

# Should see: X-Request-ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### Development vs Production

- **Development:** Docker Compose runs API and database only. Access API directly on port 8000.
- **Production:** System nginx proxies public traffic (ports 80/443) to API on localhost:8000. Docker nginx is intentionally disabled to comply with infrastructure architecture (see `ADR_SYSTEM_NGINX.md`).

---

## SSL/TLS Setup (Production Only)

For production deployments with public access, enable HTTPS using system nginx and Let's Encrypt.

**Note:** This section applies only to production deployments where system nginx is configured as the reverse proxy. For development, the API is accessed directly on port 8000 without TLS.

### 1. Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Configure System Nginx

Create a system nginx configuration file for your domain:

```bash
sudo nano /etc/nginx/conf.d/api.yourdomain.com.conf
```

Add the following configuration (HTTP only, for initial setup):

```nginx
server {
  listen 80;
  server_name api.yourdomain.com;

  location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }
}
```

### 3. Test and Reload Nginx

```bash
# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### 4. Obtain SSL Certificate

Use certbot with the nginx plugin for zero-downtime certificate issuance:

```bash
sudo certbot --nginx -d api.yourdomain.com

# Follow the prompts to complete verification
```

Certbot will automatically:
- Obtain the certificate from Let's Encrypt
- Update your nginx configuration to use HTTPS
- Add an HTTP → HTTPS redirect
- Configure SSL settings

### 5. Verify HTTPS

```bash
curl https://api.yourdomain.com/healthz
```

### 6. Certificate Auto-Renewal

Let's Encrypt certificates expire after 90 days. Certbot sets up automatic renewal:

```bash
# Test renewal (dry run)
sudo certbot renew --dry-run

# Check renewal timer status
sudo systemctl status certbot.timer

# View renewal configuration
sudo cat /etc/cron.d/certbot
```

The renewal process runs automatically. When certificates are renewed, nginx will be reloaded automatically.

### Advanced: Manual System Nginx Configuration

If you prefer full control over the nginx configuration, you can manually create the HTTPS configuration:

```nginx
map $http_upgrade $connection_upgrade {
  default upgrade;
  ''      close;
}

server {
  listen 80;
  server_name api.yourdomain.com;
  return 301 https://$server_name$request_uri;
}

server {
  listen 443 ssl http2;
  server_name api.yourdomain.com;

  server_tokens off;

  ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_ciphers HIGH:!aNULL:!MD5;
  ssl_prefer_server_ciphers on;

  # Security headers
  add_header X-Content-Type-Options "nosniff" always;
  add_header X-Frame-Options "DENY" always;
  add_header Referrer-Policy "strict-origin-when-cross-origin" always;
  add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

  # Content Security Policy (adjust as needed)
  add_header Content-Security-Policy "default-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'self';" always;

  location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;
  }
}
```

For more details on system nginx configuration, see:
- `ADR_SYSTEM_NGINX.md` - Architecture decision and rationale
- `CODEX_SYSTEM_NGINX_FIRST.md` - Operational guide
- `nginx/templates/client_system_nginx.conf.template` - Template configuration

---

## Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service with timestamp
docker-compose logs -f --timestamps api

# Last 100 lines
docker-compose logs --tail=100 api
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart api
```

### Stop Services

```bash
# Stop all services (containers remain)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (WARNING: deletes database data)
docker-compose down -v
```

### Update Application

```bash
# Navigate to project directory
cd ~/flowbiz-ai-core

# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose up --build -d

# Verify
curl http://localhost/healthz
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
docker stats
```

### Clean Up Unused Resources

```bash
# Remove unused containers, networks, images
docker system prune -a

# Remove unused volumes (WARNING: may delete data)
docker volume prune
```

---

## Troubleshooting

### Service Won't Start

**Check logs:**
```bash
docker-compose logs api
```

**Common issues:**
- Port already in use: Change port in `docker-compose.yml`
- Environment variable errors: Check `.env` file syntax
- Database connection: Verify `APP_DATABASE_URL` matches PostgreSQL settings

### Database Connection Errors

**Verify database is healthy:**
```bash
docker-compose ps db

# Should show "healthy" status
```

**Connect to database:**
```bash
docker-compose exec db psql -U flowbiz flowbiz
```

**Reset database:**
```bash
docker-compose down
docker volume rm flowbiz-ai-core_postgres-data
docker-compose up -d
```

### Nginx Returns 502 Bad Gateway

**This error occurs when system nginx cannot connect to the API service.**

**Check API service:**
```bash
docker-compose logs api

# Verify API is running
docker-compose ps api
```

**Test API directly:**
```bash
# Test from the host
curl http://localhost:8000/healthz

# Or from inside the container
docker-compose exec api curl http://localhost:8000/healthz
```

**Check system nginx configuration:**
```bash
# Test nginx configuration
sudo nginx -t

# Check nginx status
sudo systemctl status nginx

# View nginx error logs
sudo tail -f /var/log/nginx/error.log
```

**Verify API is listening on correct port:**
```bash
# Check if API is listening on port 8000
sudo netstat -tlnp | grep :8000
```

### Permission Denied Errors

**Fix file permissions:**
```bash
sudo chown -R $USER:$USER ~/flowbiz-ai-core
```

**Fix Docker socket permissions:**
```bash
# The correct method is to add the user to the docker group.
sudo usermod -aG docker $USER
# Then apply the new group membership (log out and back in, or use newgrp).
newgrp docker
```

### High Memory Usage

**Check resource usage:**
```bash
docker stats

# Limit container memory in docker-compose.yml:
services:
  api:
    deploy:
      resources:
        limits:
          memory: 512M
```

### View Container Shell

**Access API container:**
```bash
docker-compose exec api bash
```

**Access database container:**
```bash
docker-compose exec db bash
```

### Network Issues

**Inspect Docker network:**
```bash
docker network ls
docker network inspect flowbiz-ai-core_default
```

**Test inter-service connectivity:**
```bash
docker-compose exec api ping db
```

### Reset Entire Deployment

**WARNING: This deletes all data**

```bash
# Stop and remove everything
docker-compose down -v

# Remove images
docker rmi flowbiz-ai-core:dev

# Start fresh
docker-compose up --build -d
```

---

## Production Checklist

Before going live, ensure:

- [ ] Strong database password set in `.env`
- [ ] `.env` file has restrictive permissions (600)
- [ ] Firewall configured (ufw enabled, ports 80/443 open)
- [ ] SSL/TLS certificate installed and configured (system nginx)
- [ ] System nginx configured as reverse proxy (see `ADR_SYSTEM_NGINX.md`)
- [ ] Domain DNS configured correctly
- [ ] CORS origins updated for production domain
- [ ] `APP_ENV` set to `production`
- [ ] Log level appropriate (`INFO` or `WARNING`)
- [ ] Database backups scheduled
- [ ] Monitoring and alerting configured
- [ ] System updates applied
- [ ] Docker images use specific version tags (not `latest`)
- [ ] Health check endpoints accessible
- [ ] Request IDs appearing in logs

---

## Additional Resources

- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose Documentation**: https://docs.docker.com/compose/
- **Nginx Documentation**: https://nginx.org/en/docs/
- **Let's Encrypt**: https://letsencrypt.org/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

---

## Support

For issues specific to FlowBiz AI Core:
- Check repository issues: https://github.com/natbkgift/flowbiz-ai-core/issues
- Review architecture documentation: `docs/ARCHITECTURE.md`
- Review PR log: `docs/PR_LOG.md`

For infrastructure issues:
- Docker community: https://forums.docker.com/
- DigitalOcean community: https://www.digitalocean.com/community/
- Stack Overflow: https://stackoverflow.com/

---

## Next Steps

After successful deployment:

1. **Set up monitoring**: Configure log aggregation and metrics collection
2. **Implement backups**: Automate database and configuration backups
3. **Configure alerts**: Set up health check monitoring and alerting
4. **Scale horizontally**: Add load balancer and multiple API instances
5. **Add authentication**: Implement API authentication and authorization
6. **Enable rate limiting**: Protect against abuse and DoS attacks

Refer to `docs/ARCHITECTURE.md` for system architecture details and future enhancement plans.
