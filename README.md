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

   Copy `.env.example` to `.env` and adjust values as needed for your setup. The defaults are suitable for local development. All application settings are prefixed with `APP_` (for example: `APP_ENV`, `APP_NAME`, `APP_LOG_LEVEL`, `APP_DATABASE_URL`, `APP_ALLOWED_ORIGINS`, `APP_API_HOST`, `APP_API_PORT`).

The API currently exposes a minimal root endpoint and will expand in later PRs.
