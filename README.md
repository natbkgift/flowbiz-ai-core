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

   Copy `.env.example` to `.env` and adjust values as needed for your setup. The defaults are suitable for local development.

The API currently exposes a minimal root endpoint and will expand in later PRs.

## Docker

1. Build image

   ```bash
   docker build -t flowbiz-ai-core:dev .
   ```

2. Run container

   ```bash
   docker run --rm -p 8000:8000 --env-file .env flowbiz-ai-core:dev
   ```

3. Verify endpoints

   ```bash
   curl -s http://127.0.0.1:8000/healthz
   curl -s http://127.0.0.1:8000/v1/meta
   ```

Notes:
- Ensure Docker Desktop is running. On Windows, enable WSL2 backend for best performance.
- Do not commit `.env` (already ignored by `.gitignore`).
