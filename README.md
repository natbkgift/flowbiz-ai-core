# flowbiz-ai-core

FlowBiz AI Core is the foundational service layer for flowbiz.cloud. This repository uses a simple monorepo layout to host the API gateway and shared packages.

## Project structure

- `apps/api/` – FastAPI application entrypoint and related modules
- `packages/core/` – Shared core utilities and domain modules
- `infra/` – Infrastructure and deployment assets (placeholder)
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

4. **Configure environment**

   Copy `.env.example` to `.env` and adjust values as needed for your setup. The defaults are suitable for local development. Environment variables use the `APP_` prefix. Example CORS configuration:

   ```bash
   APP_CORS_ALLOW_ORIGINS=https://example.com,http://localhost:3000
   APP_CORS_ALLOW_METHODS=GET,POST
   APP_CORS_ALLOW_HEADERS=Content-Type,Authorization
   APP_CORS_ALLOW_CREDENTIALS=false
   ```

The API currently exposes a minimal root endpoint and will expand in later PRs.
