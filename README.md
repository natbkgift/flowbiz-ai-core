# flowbiz-ai-core

FlowBiz AI Core is the foundational service layer for flowbiz.cloud. This repository uses a simple monorepo layout to host the API gateway and shared packages.

## Documentation

- **[Architecture](docs/ARCHITECTURE.md)** – System design, layers, data flow, configuration, logging, and infrastructure
- **[Deployment Guide](docs/DEPLOYMENT_VPS.md)** – Step-by-step VPS deployment with Docker Compose and Nginx
- **[PR Log](docs/PR_LOG.md)** – History of pull requests (PR-001 to PR-120)

## Project structure

- `apps/api/` – FastAPI application entrypoint and related modules
- `packages/core/` – Shared core utilities and domain modules
- `docs/` – Project documentation
- `tests/` – Automated tests

## Branching conventions

- Default branch: `main`
- Feature branches: `feature/PR-<number>-<slug>` (example: `feature/PR-001-init-monorepo`)

## Getting started

1. **Install dependencies**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   ```

2. **Run the API (development)**

   ```bash
   uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Lint**

   ```bash
   ruff check .
   ```

4. **Run tests**

   ```bash
   pytest
   ```

## Continuous integration

GitHub Actions runs Ruff and pytest on every push and pull request to ensure changes remain healthy.

5. **Configure environment**

   Copy `.env.example` to `.env` and adjust values as needed for your setup. The defaults are suitable for local development. Most environment variables use the `APP_` prefix, while version metadata now prefers `FLOWBIZ_VERSION`, `FLOWBIZ_GIT_SHA`, and `FLOWBIZ_BUILD_TIME` (with legacy `APP_VERSION`/`GIT_SHA`/`BUILD_TIME` still supported). Example CORS configuration:

   Application settings are strict and only read variables with the `APP_` prefix. Version and build metadata must use the `FLOWBIZ_*` variables above (or their legacy fallbacks) and will not be consumed by `AppSettings`.

   ```bash
   APP_CORS_ALLOW_ORIGINS=https://example.com,http://localhost:3000
   APP_CORS_ALLOW_METHODS=GET,POST
   APP_CORS_ALLOW_HEADERS=Content-Type,Authorization
   APP_CORS_ALLOW_CREDENTIALS=false
   ```

The API currently exposes a minimal root endpoint and will expand in later PRs.

## Docker usage

Build and run the FastAPI service in Docker:

```bash
docker build -t flowbiz-ai-core .
docker run --rm -d --name flowbiz-ai-core-app -p 8000:8000 --env-file .env flowbiz-ai-core
```

Verify the container is healthy:

```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/v1/meta
```

## Docker Compose (API + PostgreSQL + Nginx)

Start the full stack locally:

```bash
cp .env.example .env
docker compose up --build -d
```

Verify endpoints through the Nginx reverse proxy:

```bash
curl http://127.0.0.1/healthz
curl http://127.0.0.1/v1/meta
```

Check that security headers are returned. Content-Security-Policy is enabled only when CSP values are set (keep them empty in development):

```bash
curl -I http://127.0.0.1/healthz
```

Stop the stack:

```bash
docker compose down
```

Notes:
- PostgreSQL data persists in the `postgres-data` volume
- Compose waits for db healthcheck before starting the API
- Nginx reverse proxy listens on port 80 and forwards requests to the API service
- All requests are proxied with standard headers (Host, X-Real-IP, X-Forwarded-For, X-Forwarded-Proto)
- WebSocket connections are supported through the proxy

### Security Headers & CSP

- Security headers are always enabled at Nginx.
- Path-specific Content-Security-Policy (CSP) is enabled **only in production** via environment variables.

Dev (keep CSP disabled for easy Swagger usage):

```bash
CSP_API=""
CSP_DOCS=""
```

Prod (strict for API, relaxed for Swagger):

```bash
CSP_API="default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'; object-src 'none'; img-src 'self'; connect-src 'self'; style-src 'self'; script-src 'self'"
CSP_DOCS="default-src 'self'; base-uri 'self'; frame-ancestors 'none'; object-src 'none'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'"
```

Recommended production run command with override file:

```bash
docker compose -f docker-compose.yml -f docker-compose.override.prod.yml up --build -d
```

Verify:

```bash
curl -I http://127.0.0.1/healthz | grep -i content-security-policy
curl -I http://127.0.0.1/docs | grep -i content-security-policy
```
