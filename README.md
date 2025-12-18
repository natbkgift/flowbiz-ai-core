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

3. **Run tests**

   ```bash
   pytest
   ```

## Continuous integration

GitHub Actions runs the test suite (pytest) on every push and pull request to ensure changes remain healthy.

4. **Configure environment**

   Copy `.env.example` to `.env` and adjust values as needed for your setup. The defaults are suitable for local development. Environment variables use the `APP_` prefix. Example CORS configuration:

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
