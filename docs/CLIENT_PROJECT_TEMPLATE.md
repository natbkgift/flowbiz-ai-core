# FlowBiz Client Project Template

**วัตถุประสงค์:** Template นี้ใช้สำหรับสร้างโปรเจคลูกค้าที่เชื่อมต่อกับ FlowBiz AI Core ได้อย่างราบรื่น รองรับการ deploy บน VPS และใช้โครงสร้างมาตรฐานเดียวกัน

---

## 🚧 Status: Template Status Tracker

**Copy this section into your project README.md and track progress:**

```markdown
## 📊 Project Readiness Checklist

### Phase 1: Core Structure ✅/⏳
- [ ] README.md created
- [ ] docker-compose.yml setup
- [ ] Dockerfile configured
- [ ] pyproject.toml with dependencies
- [ ] .env.example configured

### Phase 2: Contract Implementation ⏳
- [ ] GET /healthz endpoint (returns 200 + JSON)
- [ ] GET /v1/meta endpoint (with version/build_sha)
- [ ] [Business endpoint 1] _______________
- [ ] [Business endpoint 2] _______________
- [ ] [Business endpoint 3] _______________

### Phase 3: Documentation ⏳
- [ ] docs/PROJECT_CONTRACT.md
- [ ] docs/DEPLOYMENT.md
- [ ] docs/GUARDRAILS.md
- [ ] docs/CODEX_PREFLIGHT.md

### Phase 4: CI/CD & Security ⏳
- [ ] .github/workflows/ci.yml
- [ ] .github/workflows/guardrails.yml
- [ ] .github/workflows/pr-labels.yml
- [ ] .github/workflows/deploy.yml (with GitHub Secrets)
- [ ] nginx/templates/default.conf.template
- [ ] nginx/snippets/security_headers.conf

### Phase 5: Testing & Validation ⏳
- [ ] `docker compose up` runs without errors
- [ ] `curl http://localhost:8001/healthz` → 200 OK
- [ ] `curl http://localhost:8001/v1/meta` → 200 OK
- [ ] Business endpoints respond correctly
- [ ] `ruff check .` passes
- [ ] `pytest -q` passes

### Phase 6: Deployment Setup ⏳
- [ ] VPS DNS configured (A record pointing to IP)
- [ ] GitHub Secrets configured (DEPLOY_SSH_KEY, DEPLOY_VPS_IP)
- [ ] SSH key added to VPS authorized_keys
- [ ] Docker Compose prod override tested
- [ ] HTTPS certificate provisioned (Let's Encrypt)

### Phase 7: Go Live ⏳
- [ ] `git push origin main` triggers auto-deploy
- [ ] `curl https://[domain]/healthz` → 200 OK
- [ ] `curl https://[domain]/v1/meta` → 200 OK
- [ ] Security headers present in responses
- [ ] Monitoring/alerts configured (optional)

---

## 📝 Status Indicators

| Status | Meaning | Action |
|--------|---------|--------|
| ✅ | Complete | Ready to use |
| ⏳ | In Progress | Agent working on it |
| ❌ | Blocked | Owner intervention needed |
| 🚧 | Draft/Partial | Not production-ready yet |

## Usage Rules

- **🚧 DRAFT:** Use this template only if Phases 1-2 complete
- **👷 IN DEVELOPMENT:** Share this repo only with Agent if Phases 1-5 complete
- **🟢 PRODUCTION READY:** Deploy to VPS only if all 7 phases complete + CI green
```

---

## 🎯 Agent Kickoff Packet (Copy-Paste Ready)

```markdown
# Project Setup Request

## 1. Project Goal
[ระบุชื่อโปรเจค + วัตถุประสงค์หลัก 1-2 ประโยค]

ตัวอย่าง: "Customer Support Bot API — REST API สำหรับจัดการ conversation และ ticket routing โดยเชื่อมกับ FlowBiz AI Core"

## 2. Must-Have Endpoints (FlowBiz Contract)

### Health & Metadata (Required)
- `GET /healthz` → `200 OK` + `{"status": "ok", "service": "service-name", "version": "x.y.z"}`
- `GET /v1/meta` → `{"service": "service-name", "environment": "dev/prod", "version": "x.y.z", "build_sha": "abc123"}`

### Business Endpoints (Minimal)
[ระบุ 2-3 endpoints หลักที่ต้องมี เช่น]
- `POST /v1/conversations` — สร้าง conversation ใหม่
- `GET /v1/conversations/{id}` — ดึงข้อมูล conversation
- `POST /v1/conversations/{id}/messages` — ส่งข้อความ

## 3. Environment Variables Rules

### APP_* (Application Settings - Strict)
```bash
APP_SERVICE_NAME=customer-support-api
APP_ENV=dev
APP_LOG_LEVEL=INFO
APP_CORS_ORIGINS=["http://localhost:3000"]
```

### FLOWBIZ_* (Metadata - Read by core/deployment)
```bash
FLOWBIZ_VERSION=0.1.0
FLOWBIZ_BUILD_SHA=local-dev
```

### Integration (ถ้าเชื่อม core)
```bash
FLOWBIZ_CORE_URL=http://localhost:8000
FLOWBIZ_API_KEY=secret-key
```

## 4. Run Modes (Required Support)

### Local Development
```bash
python -m uvicorn apps.api.main:app --reload --port 8001
```

### Docker Compose (Dev)
```bash
docker compose up --build
```

### Docker Compose (Production Override)
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 5. Deployment Target

- **Platform:** Hostinger VPS Ubuntu 24.04
- **Domain:** [ระบุ domain หรือ subdomain]
- **SSL:** Let's Encrypt via Certbot
- **Reverse Proxy:** Nginx (ต้องมี security headers)
- **Port:** Internal 8001, External 443 (HTTPS)

## 6. Guardrails (Same as flowbiz-ai-core)

- Non-blocking CI (ruff + pytest)
- PR comment bot for missing persona/description
- Codex pre-flight checklist (mandatory before code)
- Persona labels: `persona:core` / `persona:infra` / `persona:docs`

---

## 📋 Repository Contract (Files You MUST Create)

### 1. README.md
```markdown
# [Project Name]

## Goal
[1-2 ประโยคอธิบายโปรเจค]

## Runtime Targets
- Local: `http://localhost:8001`
- Docker: `http://localhost:8001`
- Production: `https://[domain]`

## Entrypoints
- Health: `GET /healthz`
- Metadata: `GET /v1/meta`
- [ระบุ business endpoints อื่น ๆ]

## Environment Variables
**APP_* (Strict):**
- `APP_SERVICE_NAME` — ชื่อ service
- `APP_ENV` — `dev` / `staging` / `prod`
- `APP_LOG_LEVEL` — `DEBUG` / `INFO` / `WARNING` / `ERROR`
- `APP_CORS_ORIGINS` — JSON array ของ allowed origins

**FLOWBIZ_* (Metadata):**
- `FLOWBIZ_VERSION` — Version string (e.g., `0.1.0`)
- `FLOWBIZ_BUILD_SHA` — Git commit SHA (or `local-dev`)

## How to Run

### Local
```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
uvicorn apps.api.main:app --reload --port 8001
```

### Docker
```bash
docker compose up --build
```

### Production (VPS)
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Smoke Tests
```bash
# Health check
curl http://localhost:8001/healthz

# Metadata
curl http://localhost:8001/v1/meta

# [ระบุ business endpoint test]
curl -X POST http://localhost:8001/v1/[resource] -H "Content-Type: application/json" -d '{"key": "value"}'
```
```

### 2. docs/PROJECT_CONTRACT.md
```markdown
# Project Contract

This document defines the **integration contract** between this service and FlowBiz AI Core / deployment infrastructure.

## API Contract

### Required Endpoints
1. `GET /healthz`
   - Response: `200 OK`
   - Body: `{"status": "ok", "service": "service-name", "version": "x.y.z"}`
   - Purpose: Load balancer health check

2. `GET /v1/meta`
   - Response: `200 OK`
   - Body: `{"service": "...", "environment": "...", "version": "...", "build_sha": "..."}`
   - Purpose: Runtime metadata for observability

### Response Schema Standards
- Use `BaseSchema` from `packages.core.schemas.base` if integrating with core
- All responses must include `request_id` in error cases
- All timestamps in ISO 8601 format with timezone

### Logging & Tracing
- Every request must generate a `trace_id` or `request_id`
- Log format: JSON structured logging (compatible with core)
- Log keys: `timestamp`, `level`, `service`, `request_id`, `message`

### Security Headers (if behind Nginx)
Required headers in responses:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- (Production) `Strict-Transport-Security: max-age=31536000; includeSubDomains`

### Version Metadata
- `FLOWBIZ_VERSION` env var MUST be read and exposed in `/v1/meta`
- `FLOWBIZ_BUILD_SHA` (optional) should be included if available
- Version format: Semantic versioning (e.g., `0.1.0`, `1.2.3`)

### Error Format
All errors must return:
```json
{
  "detail": "Error message",
  "request_id": "uuid-or-trace-id",
  "timestamp": "2025-12-24T10:30:00Z"
}
```

Standard status codes:
- `400` — Bad Request (client error)
- `404` — Not Found
- `422` — Validation Error
- `500` — Internal Server Error
```

### 3. docs/DEPLOYMENT.md
```markdown
# Deployment Guide

## Local Development
```bash
cp .env.example .env
# Edit .env with local values
docker compose up --build
```

## Production Deployment (VPS)

### Prerequisites
- Ubuntu 24.04 server with Docker + Docker Compose installed
- Domain/subdomain pointing to server IP
- SSL certificate (Let's Encrypt via Certbot)

### Steps
1. **Clone repository**
   ```bash
   git clone https://github.com/[org]/[repo].git
   cd [repo]
   ```

2. **Set environment variables**
   ```bash
   cp .env.example .env.prod
   nano .env.prod  # Edit with production values
   ```

3. **Configure Nginx**
   - Ensure `nginx/templates/default.conf.template` has correct domain
   - SSL certificates should be in `/etc/letsencrypt/live/[domain]/`

4. **Start services**
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

5. **Verify**
   ```bash
   curl https://[domain]/healthz
   curl https://[domain]/v1/meta
   ```

### Reverse Proxy Assumptions
- Nginx runs as reverse proxy in same Docker network
- Service listens on internal port (e.g., 8001)
- Nginx exposes 443 (HTTPS) externally
- HTTP (80) redirects to HTTPS

### Domain & SSL Strategy
- Domain: Managed via domain provider DNS (A record → server IP)
- SSL: Let's Encrypt certificates
- Renewal: Certbot auto-renewal via cron
- Certificate path: `/etc/letsencrypt/live/[domain]/`

### Data Persistence
- Application data: Docker volume `app-data`
- Logs: Docker volume `app-logs`
- Nginx config: Mounted from `./nginx/templates/`
```

### 4. docs/GUARDRAILS.md
```markdown
# Guardrails

เอกสารนี้กำหนดกฎการทำงานของโปรเจค โดยเป็น **non-blocking** ใน CI แต่มี automated PR comment bot และ pre-flight checklist บังคับ

## CI Enforcement (Non-blocking)
- Guardrails checks ไม่ fail CI build
- PR comment bot จะโพสต์ feedback อัตโนมัติ
- Pre-flight checklist ต้องกรอกก่อนเขียนโค้ด

### PR Comment Bot
Bot จะตรวจสอบและแจ้ง:
- Missing persona label (`persona:core` / `persona:infra` / `persona:docs`)
- Missing PR description sections (Summary, Testing)
- Quick fix instructions

Bot ใช้ marker: `<!-- flowbiz-guardrails-bot -->`

### Persona Label Requirement
ทุก PR ต้องมี label หนึ่งอัน:
- `persona:core` — Core logic และ business rules
- `persona:infra` — Infrastructure, deployment, operations
- `persona:docs` — Documentation updates

### PR Description Requirements (Minimum)
- `## Summary` — อธิบายการเปลี่ยนแปลง
- `## Testing` — วิธีที่ verify การเปลี่ยนแปลง (commands, manual steps)

Template เต็มมีใน `.github/pull_request_template.md`

## Pre-Flight Checklist
ดู `docs/CODEX_PREFLIGHT.md` — ต้องตอบก่อนเขียนโค้ดทุกครั้ง
```

### 5. docs/CODEX_PREFLIGHT.md
```markdown
# Codex Pre-Flight Checklist

**MANDATORY: กรอกก่อนเขียนโค้ดทุกครั้ง**

## PR-021.2 — Codex Pre-flight (ต้องตอบก่อนเริ่มงาน)

### Persona (เลือก 1 อัน)
- [ ] persona:core
- [ ] persona:infra
- [ ] persona:docs

### Scope Lock 🔒
- **Goal (1 ประโยค):** `<ระบุเป้าหมาย>`
- **In-scope files:** `<ระบุไฟล์ที่จะแก้>`
- **Out-of-scope (3 ข้อ):**
  1. `<สิ่งที่จะไม่แตะ>`
  2. `<สิ่งที่จะไม่แตะ>`
  3. `<สิ่งที่จะไม่แตะ>`
- **Behavior changes:**
  - [ ] ไม่มี
  - [ ] มี (อธิบาย): `<ระบุสั้น ๆ>`

### Evidence (บังคับ)
- **PR description อ่านแล้ว:** [ ]
- **CI failures อ่านแล้ว (ถ้ามี):** [ ]
- **Logs/stack trace:** `<แปะที่สำคัญ หรือ N/A>`

### Plan (สูงสุด 5 ขั้นตอน)
1. `<ขั้นตอน 1>`
2. `<ขั้นตอน 2>`
3. `<ขั้นตอน 3>`
4. `<ขั้นตอน 4>`
5. `<ขั้นตอน 5>`

### Commands ที่จะรันในเครื่อง
- [ ] `ruff check .`
- [ ] `pytest -q`
- [ ] Smoke command (ถ้ามี): `<ระบุ หรือ N/A>`

### Safety
- **เพิ่ม dependencies ใหม่?**
  - [ ] ไม่
  - [ ] ใช่ — ระบุ + เหตุผล: `<package และทำไม>`
- **แตะ secrets/env?**
  - [ ] ไม่
  - [ ] ใช่ — อธิบาย: `<อะไรและทำไม>`

### Exit Criteria
- [ ] CI เขียวใน PR
- [ ] Summary + Testing กรอกครบใน PR body
- [ ] ไม่มี scope creep
```

### 6. .env.example
```bash
# Application Settings (Strict - validated by pydantic)
APP_SERVICE_NAME=my-service
APP_ENV=dev
APP_LOG_LEVEL=INFO
APP_CORS_ORIGINS=["http://localhost:3000"]

# FlowBiz Metadata (Read by core/deployment)
FLOWBIZ_VERSION=0.1.0
FLOWBIZ_BUILD_SHA=local-dev

# Integration (ถ้าเชื่อมกับ core)
# FLOWBIZ_CORE_URL=http://localhost:8000
# FLOWBIZ_API_KEY=your-api-key-here

# Database (ถ้ามี)
# DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# External Services (ถ้ามี)
# EXTERNAL_API_KEY=your-key
# EXTERNAL_API_URL=https://api.example.com
```

### 7. docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8001:8000"
    environment:
      APP_SERVICE_NAME: ${APP_SERVICE_NAME}
      APP_ENV: ${APP_ENV}
      APP_LOG_LEVEL: ${APP_LOG_LEVEL}
      APP_CORS_ORIGINS: ${APP_CORS_ORIGINS}
      FLOWBIZ_VERSION: ${FLOWBIZ_VERSION}
      FLOWBIZ_BUILD_SHA: ${FLOWBIZ_BUILD_SHA}
    volumes:
      - ./apps:/app/apps
      - ./packages:/app/packages
    command: uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/templates:/etc/nginx/templates
      - ./nginx/snippets:/etc/nginx/snippets
    environment:
      NGINX_HOST: localhost
      NGINX_PORT: 80
      UPSTREAM_HOST: app
      UPSTREAM_PORT: 8000
    depends_on:
      - app
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

### 8. docker-compose.prod.yml
```yaml
version: '3.8'

services:
  app:
    restart: always
    environment:
      APP_ENV: prod
      APP_LOG_LEVEL: WARNING
    command: uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --workers 4

  nginx:
    restart: always
    ports:
      - "443:443"
      - "80:80"  # Redirect to 443
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro
    environment:
      NGINX_HOST: ${DOMAIN}
      NGINX_PORT: 443
```

---

## 🗂️ Repository Skeleton (Recommended Structure)

```
my-service/
├── .github/
│   ├── CODEOWNERS
│   ├── pull_request_template.md
│   ├── scripts/
│   │   └── validate_pr_template.py
│   └── workflows/
│       ├── ci.yml
│       ├── guardrails.yml
│       └── pr-labels.yml
├── apps/
│   └── api/
│       ├── __init__.py
│       ├── main.py
│       ├── middleware.py
│       └── routes/
│           ├── __init__.py
│           ├── health.py
│           └── v1/
│               ├── __init__.py
│               └── meta.py
├── packages/
│   └── core/
│       ├── __init__.py
│       ├── config.py
│       ├── logging.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── error.py
│       │   └── health.py
│       └── services/
│           └── __init__.py
├── nginx/
│   ├── templates/
│   │   └── default.conf.template
│   └── snippets/
│       ├── proxy_headers.conf
│       └── security_headers.conf
├── docs/
│   ├── PROJECT_CONTRACT.md
│   ├── DEPLOYMENT.md
│   ├── GUARDRAILS.md
│   └── CODEX_PREFLIGHT.md
├── scripts/
│   └── guardrails_pr_check.py
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   └── test_meta.py
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

---

## 🔌 Integration Contract Summary

### Minimum Endpoints
- `GET /healthz` → `{"status": "ok", "service": "...", "version": "..."}`
- `GET /v1/meta` → `{"service": "...", "environment": "...", "version": "...", "build_sha": "..."}`

### Minimum Headers (Nginx)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- (Prod) `Strict-Transport-Security: max-age=31536000; includeSubDomains`

### Versioning
- Read `FLOWBIZ_VERSION` from env
- Read `FLOWBIZ_BUILD_SHA` from env (optional)
- Expose in `/v1/meta`

### Error Shape
```json
{
  "detail": "Error message",
  "request_id": "uuid",
  "timestamp": "2025-12-24T10:30:00Z"
}
```

---

## 📦 Quick Start Commands

### 1. Copy Template to New Repo
```bash
# ใช้ GitHub "Use this template" button หรือ
git clone https://github.com/natbkgift/flowbiz-template-service.git my-new-service
cd my-new-service
rm -rf .git
git init
git remote add origin https://github.com/[org]/my-new-service.git
```

### 2. Update Project-Specific Values
```bash
# แก้ใน README.md, pyproject.toml, .env.example
# ค้นหา "my-service" แล้วแทนที่ด้วยชื่อโปรเจคจริง
find . -type f -name "*.md" -o -name "*.toml" -o -name "*.yml" | xargs sed -i 's/my-service/actual-service-name/g'
```

### 3. Run Local Tests
```bash
cp .env.example .env
docker compose up --build
curl http://localhost:8001/healthz
curl http://localhost:8001/v1/meta
```

### 4. Deploy to Production
```bash
# On VPS
git clone https://github.com/[org]/my-new-service.git
cd my-new-service
cp .env.example .env.prod
nano .env.prod  # Edit production values
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## � VPS Access & Deployment (for Agents)

### SSH Key Access via GitHub Secrets (Recommended ⭐)

**Step 1: Owner/DevOps Setup VPS** (one-time):
```bash
ssh root@[VPS-IP]

# Create agent-specific SSH key
ssh-keygen -t ed25519 -f ~/.ssh/id_flowbiz_agent_[project-name] -N ""

# Add public key to authorized_keys
cat ~/.ssh/id_flowbiz_agent_[project-name].pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Verify SSH config
sudo nano /etc/ssh/sshd_config
# PermitRootLogin prohibit-password    ← key-based only
# PasswordAuthentication no             ← no password login
# PubkeyAuthentication yes              ← enable keys

sudo systemctl restart ssh
```

**Step 2: Store Private Key in GitHub Secrets** (owner only):
```bash
# Copy private key
cat ~/.ssh/id_flowbiz_agent_[project-name]

# Go to: GitHub repo → Settings → Secrets and variables → New repository secret
# DEPLOY_SSH_KEY = [entire private key]
# DEPLOY_VPS_IP = [VPS IP address]
```

**Step 3: Create `.github/workflows/deploy.yml`**:
```yaml
name: Deploy to VPS

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.DEPLOY_SSH_KEY }}" > ~/.ssh/id_deploy
          chmod 600 ~/.ssh/id_deploy
          ssh-keyscan -H ${{ secrets.DEPLOY_VPS_IP }} >> ~/.ssh/known_hosts
      
      - name: Deploy
        run: |
          ssh -i ~/.ssh/id_deploy root@${{ secrets.DEPLOY_VPS_IP }} << 'EOF'
          cd /opt/projects/[project-name]
          git pull origin main
          docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
          echo "✅ Deployed"
          EOF
      
      - name: Verify health
        run: curl -f https://[domain]/healthz
```

**Step 4: Agent Triggers Deployment**:
```bash
git push origin main
# GitHub Actions automatically deploys! No manual SSH needed.
```

### Why GitHub Secrets?
- ✅ Private key encrypted in GitHub (never in chat)
- ✅ Access control via GitHub Org/Team
- ✅ Audit trail of deployments
- ✅ Fully automated (push to main = deploy)
- ✅ Easy key rotation (update secret + regenerate)

---

## �💡 Best Practices

1. **ใช้ Template Repo**
   - สร้าง `flowbiz-template-service` repository
   - ใส่โครงสร้างพื้นฐานทั้งหมด
   - ใช้ "Use this template" เวลาเริ่มโปรเจคใหม่

2. **ตรวจสอบ Contract ก่อน Deploy**
   - `/healthz` ต้องตอบ 200 เสมอ
   - `/v1/meta` ต้องมี version ถูกต้อง
   - Security headers ครบ (ใน production)

3. **Sync Guardrails กับ Core**
   - ใช้ workflow เดียวกัน (non-blocking)
   - ใช้ pre-flight checklist เดียวกัน
   - ใช้ persona labels เดียวกัน

4. **Document Everything**
   - `README.md` — Quick start
   - `PROJECT_CONTRACT.md` — Integration rules
   - `DEPLOYMENT.md` — Production deployment
   - `CODEX_PREFLIGHT.md` — Agent instructions

---

## 🚀 สิ่งที่ต้องส่งให้ Agent (One-Liner)

**Copy-paste นี้ในแชท AI อื่น:**

```
สร้างโปรเจค [ชื่อโปรเจค] ตาม FlowBiz Client Project Template:
https://github.com/natbkgift/flowbiz-ai-core/blob/main/docs/CLIENT_PROJECT_TEMPLATE.md

ต้องการ:
1. Endpoints: /healthz, /v1/meta + [ระบุ business endpoints]
2. Env: APP_* strict, FLOWBIZ_* metadata
3. Deploy: Docker Compose (dev + prod override), Hostinger VPS Ubuntu 24.04
4. Guardrails: Non-blocking CI + PR comment bot + pre-flight checklist
5. Integration: เชื่อมกับ core ที่ http://localhost:8000 (ถ้าต้องการ)

ดู template ครบที่ลิงก์ด้านบน แล้วสร้างให้ครบทุกไฟล์ตาม Repository Skeleton
```

---

## ✅ Checklist สำหรับ Validation

เมื่อโปรเจคลูกค้าสร้างเสร็จ ตรวจสอบ:

- [ ] README.md มี quick start ครบ
- [ ] docs/PROJECT_CONTRACT.md ระบุ contract ชัดเจน
- [ ] docs/DEPLOYMENT.md มีขั้นตอน deploy VPS
- [ ] docs/GUARDRAILS.md + CODEX_PREFLIGHT.md ครบ
- [ ] .env.example มีคีย์ครบ แยก APP_* กับ FLOWBIZ_*
- [ ] docker-compose.yml + docker-compose.prod.yml พร้อม
- [ ] `/healthz` ตอบ 200 + JSON ถูกต้อง
- [ ] `/v1/meta` แสดง version + build_sha
- [ ] nginx security headers ครบ (prod)
- [ ] ruff check + pytest ผ่าน
- [ ] CI workflows (guardrails.yml, pr-labels.yml) ทำงาน

---

**ที่มา:** `flowbiz-ai-core/docs/CLIENT_PROJECT_TEMPLATE.md`  
**อัปเดตล่าสุด:** 2025-12-24  
**Maintainer:** FlowBiz AI Core Team
```
