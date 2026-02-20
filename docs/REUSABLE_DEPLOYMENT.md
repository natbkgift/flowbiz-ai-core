# Reusable VPS Deployment Workflow

This repository provides a **reusable GitHub Actions workflow** for deploying Docker Compose projects to VPS servers. Other projects can use this workflow without copying SSH keys or deployment scripts.

## 🔒 Security Features

- ✅ SSH keys stored in GitHub Secrets (encrypted)
- ✅ Environment protection rules (approval, branch restrictions)
- ✅ Audit logs for all deployments
- ✅ Secrets inheritance (projects don't hold keys directly)
- ✅ No credentials in code or repositories

## 📋 Setup Guide

### Step 1: Configure GitHub Secrets (One-time setup)

Create a GitHub **Environment** named `vps-prod` in your organization or repository:

1. Go to **Settings** → **Environments** → **New environment**
2. Name it: `vps-prod`
3. Add **Environment secrets**:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `VPS_HOST` | VPS IP or domain | `203.0.113.45` or `api.example.com` |
| `VPS_USER` | SSH username | `flowbiz` |
| `VPS_SSH_KEY` | Private SSH key (PEM format) | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `VPS_PORT` | SSH port (optional) | `22` (default) |
| `VPS_URL` | Deployment URL (optional) | `https://api.example.com` |

4. **Enable Environment Protection** (Recommended):
   - ✅ Required reviewers: Add team members who can approve deployments
   - ✅ Deployment branches: Restrict to `main` or `production` only
   - ✅ Wait timer: Add delay to prevent accidental deployments

### Step 2: Use in Other Projects

Create a workflow file in your project: `.github/workflows/deploy.yml`

```yaml
name: Deploy to VPS

on:
  workflow_dispatch:
    inputs:
      remote_path:
        description: 'Remote deployment path'
        required: true
        default: '/home/flowbiz/my-project'
  
  push:
    branches:
      - main

jobs:
  deploy:
    uses: natbkgift/flowbiz-ai-core/.github/workflows/deploy_vps.yml@main
    with:
      remote_path: ${{ github.event.inputs.remote_path || '/home/flowbiz/my-project' }}
      compose_files: 'docker-compose.yml docker-compose.prod.yml'
      pre_build_cmd: |
        # Optional: Run before building
        echo "Starting deployment..."
      post_deploy_cmd: |
        # Optional: Health check after deployment
        sleep 5
        docker compose ps
        curl -f http://localhost:8000/health || echo "Health check pending..."
      docker_prune: true
    secrets: inherit
    environment: vps-prod
```

**Important:**
- Replace `natbkgift/flowbiz-ai-core` with your repo path
- Use `secrets: inherit` to access secrets from the `vps-prod` environment
- Use `environment: vps-prod` to enforce protection rules

### Step 3: Deploy

**Manual deployment:**
```bash
# Go to Actions → Deploy to VPS → Run workflow
# Or use GitHub CLI:
gh workflow run deploy.yml
```

**Automatic deployment:**
- Push to `main` branch will trigger deployment automatically

## 🖥️ Local Development Setup (Windows)

For local development and manual deployments from your Windows machine:

### Option 1: SSH Config + Docker Context (Recommended)

**Step 1: Configure SSH**

Create or edit `C:\Users\<YourName>\.ssh\config`:

> Tip (Thai keyboard): ถ้าพิมพ์ `.ssh` แล้ว “จุด” (`.`) ถูกพิมพ์เป็นอักษรไทย (U+0E41) ให้สลับคีย์บอร์ดเป็น EN ก่อน หรือรัน `scripts/fix-ssh-folder.ps1` เพื่อแก้ชื่อโฟลเดอร์

```ssh-config
Host flowbiz-vps
  HostName 203.0.113.45
  User flowbiz
  Port 22
  IdentityFile C:\Users\<YourName>\.ssh\id_ed25519
  IdentitiesOnly yes
  ServerAliveInterval 60
  ServerAliveCountMax 3
```

**Step 2: Test SSH connection**

```powershell
ssh flowbiz-vps
# Should connect without password
```

**Step 3: Create Docker Context**

```powershell
# Create context pointing to VPS
docker context create flowbiz-vps --docker "host=ssh://flowbiz-vps"

# Use the context
docker context use flowbiz-vps

# Verify
docker info
# Should show your VPS details
```

**Step 4: Deploy from any project**

```powershell
# Navigate to your project
cd D:\Projects\my-app

# Deploy to VPS
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

# Switch back to local
docker context use default
```

### Option 2: Direct SSH Commands

```powershell
# Copy project to VPS
scp -r . flowbiz-vps:/home/flowbiz/my-project

# Deploy via SSH
ssh flowbiz-vps "cd /home/flowbiz/my-project && docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d"
```

## 🔐 SSH Key Setup

### Generate SSH Key (if you don't have one)

```powershell
# Generate new key
ssh-keygen -t ed25519 -C "vps-prod-deployment" -f C:\Users\<YourName>\.ssh\id_ed25519

# Add to ssh-agent (Windows)
Start-Service ssh-agent
ssh-add C:\Users\<YourName>\.ssh\id_ed25519

# Copy public key to VPS
type C:\Users\<YourName>\.ssh\id_ed25519.pub | ssh user@vps-host "cat >> ~/.ssh/authorized_keys"
```

### Protect SSH Key

```powershell
# Set proper permissions (Windows)
icacls C:\Users\<YourName>\.ssh\id_ed25519 /inheritance:r
icacls C:\Users\<YourName>\.ssh\id_ed25519 /grant:r "%USERNAME%:F"
```

## 🛡️ VPS Security Hardening

After setting up deployment, secure your VPS:

```bash
# 1. SSH Key-only authentication
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
# Set: PubkeyAuthentication yes
sudo systemctl reload sshd

# 2. Firewall setup
sudo ufw enable
sudo ufw allow from YOUR_IP to any port 22  # Restrict SSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 3. Install fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban

# 4. Protect .env files
chmod 600 .env
chown flowbiz:flowbiz .env

# 5. Regular updates
sudo apt update && sudo apt upgrade -y
```

## 📊 Workflow Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `remote_path` | Yes | - | Deployment path on VPS |
| `compose_files` | No | `docker-compose.yml docker-compose.override.prod.yml` | Compose files (space-separated) |
| `pre_build_cmd` | No | - | Commands before building |
| `post_deploy_cmd` | No | - | Commands after deployment |
| `docker_prune` | No | `true` | Clean up unused Docker resources |

## 📊 Workflow Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `VPS_HOST` | Yes | VPS hostname or IP |
| `VPS_USER` | Yes | SSH username |
| `VPS_SSH_KEY` | Yes | Private SSH key |
| `VPS_PORT` | No | SSH port (default: 22) |

## 🎯 Example Use Cases

### Use Case 1: Different Compose Files

```yaml
with:
  compose_files: 'docker-compose.yml docker-compose.staging.yml'
```

### Use Case 2: Environment-specific Commands

```yaml
with:
  pre_build_cmd: |
    cp .env.production .env
    chmod 600 .env
  post_deploy_cmd: |
    docker compose exec -T app python manage.py migrate
    docker compose exec -T app python manage.py collectstatic --noinput
```

### Use Case 3: Multiple Environments

```yaml
jobs:
  deploy-staging:
    uses: natbkgift/flowbiz-ai-core/.github/workflows/deploy_vps.yml@main
    with:
      remote_path: '/home/flowbiz/staging'
    secrets: inherit
    environment: vps-staging

  deploy-production:
    needs: deploy-staging
    uses: natbkgift/flowbiz-ai-core/.github/workflows/deploy_vps.yml@main
    with:
      remote_path: '/home/flowbiz/production'
    secrets: inherit
    environment: vps-prod
```

## 🚀 Quick Start Checklist

- [ ] Generate SSH key pair
- [ ] Add public key to VPS `~/.ssh/authorized_keys`
- [ ] Create GitHub Environment `vps-prod`
- [ ] Add secrets: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`
- [ ] Enable environment protection rules
- [ ] Create workflow file in your project
- [ ] Configure SSH config on local machine (optional)
- [ ] Create Docker context (optional)
- [ ] Test deployment manually
- [ ] Configure automatic deployment trigger

## 📚 Additional Resources

- [DEPLOYMENT_VPS.md](docs/DEPLOYMENT_VPS.md) - Detailed VPS deployment guide
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture
- [GitHub Environments Documentation](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Docker Context Documentation](https://docs.docker.com/engine/context/working-with-contexts/)

## 🆘 Troubleshooting

### Error: "Permission denied (publickey)"

```bash
# Check SSH key is added to VPS
cat ~/.ssh/authorized_keys

# Verify key permissions on local machine
ls -la ~/.ssh/
# Should be 600 for private key, 644 for public key
```

### Error: "Connection refused"

```bash
# Check if SSH service is running on VPS
sudo systemctl status sshd

# Check firewall rules
sudo ufw status
```

### Error: "Docker compose command not found"

```bash
# Install Docker Compose V2 on VPS
sudo apt update
sudo apt install docker-compose-plugin -y
docker compose version
```

## 📝 License

See [LICENSE](LICENSE) file for details.
