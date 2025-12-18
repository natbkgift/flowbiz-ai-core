# VPS Deployment Guide

This guide provides step-by-step instructions for deploying FlowBiz AI Core to a Virtual Private Server (VPS) using Docker Compose and Nginx.

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
APP_VERSION=0.1.0
APP_LOG_LEVEL=INFO

# Set GIT_SHA to current commit (optional)
GIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

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
- Pull Nginx and PostgreSQL images
- Create necessary volumes
- Start all three services (nginx, api, db)

### 2. Monitor Startup

```bash
# View logs from all services
docker-compose logs -f

# View logs from specific service
docker-compose logs -f api
docker-compose logs -f nginx
docker-compose logs -f db
```

Press `Ctrl+C` to stop following logs.

### 3. Check Service Status

```bash
# List running containers
docker-compose ps

# Expected output:
# NAME                COMMAND                  SERVICE   STATUS          PORTS
# flowbiz-nginx       "nginx -g 'daemon of…"   nginx     Up 2 minutes    0.0.0.0:80->80/tcp
# flowbiz-api         "uvicorn apps.api.ma…"   api       Up 2 minutes    8000/tcp
# flowbiz-db          "docker-entrypoint.s…"   db        Up 2 minutes    5432/tcp
```

All services should show `Up` status.

---

## Verify Deployment

### 1. Test Health Endpoint

```bash
# From VPS
curl http://localhost/healthz

# Expected response:
# {"status":"ok","service":"FlowBiz AI Core","version":"0.1.0"}
```

### 2. Test Metadata Endpoint

```bash
curl http://localhost/v1/meta

# Expected response:
# {"service":"FlowBiz AI Core","version":"0.1.0","git_sha":"abc1234"}
```

### 3. Test Root Endpoint

```bash
curl http://localhost/

# Expected response:
# {"message":"FlowBiz AI Core API"}
```

### 4. Test from External Client

From your local machine:

```bash
# Replace YOUR_VPS_IP with your server's IP
curl http://YOUR_VPS_IP/healthz

# Or with domain name
curl http://api.yourdomain.com/healthz
```

### 5. Check Request ID Header

```bash
curl -i http://localhost/healthz | grep X-Request-ID

# Should see: X-Request-ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

## SSL/TLS Setup (Optional)

For production deployments, enable HTTPS using Let's Encrypt.

### 1. Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Stop Nginx Container

```bash
docker-compose stop nginx
```

### 3. Obtain SSL Certificate

```bash
sudo certbot certonly --standalone -d api.yourdomain.com

# Follow the prompts to complete verification
```

### 4. Update Nginx Configuration

Create a new Nginx configuration for HTTPS:

```bash
nano ~/flowbiz-ai-core/nginx/nginx.conf
```

Add HTTPS server block:

```nginx
events {
    worker_connections 1024;
}

http {
    map $http_upgrade $connection_upgrade {
        default upgrade;
        '' close;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name api.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name api.yourdomain.com;

        ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        resolver 127.0.0.11 valid=30s;
        set $upstream_api api:8000;

        location / {
            proxy_pass http://$upstream_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
        }
    }
}
```

### 5. Update Docker Compose

Edit `docker-compose.yml` to mount SSL certificates:

```bash
nano docker-compose.yml
```

Update nginx service:

```yaml
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"  # Add HTTPS port
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro  # Mount certificates
    depends_on:
      - api
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/healthz"]
      interval: 10s
      timeout: 3s
      retries: 3
```

### 6. Restart Services

```bash
docker-compose up -d
```

### 7. Verify HTTPS

```bash
curl https://api.yourdomain.com/healthz
```

### 8. Set Up Certificate Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Certificates auto-renew via systemd timer
sudo systemctl status certbot.timer
```

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

**Check API service:**
```bash
docker-compose logs api

# Verify API is running
docker-compose ps api
```

**Test API directly:**
```bash
docker-compose exec api curl http://localhost:8000/healthz
```

### Permission Denied Errors

**Fix file permissions:**
```bash
sudo chown -R $USER:$USER ~/flowbiz-ai-core
```

**Fix Docker socket permissions:**
```bash
sudo chmod 666 /var/run/docker.sock
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
docker-compose exec nginx ping api
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
- [ ] SSL/TLS certificate installed and configured
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
