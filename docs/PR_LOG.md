# Pull Request Log

This document tracks the history of pull requests for FlowBiz AI Core, summarizing the goals, key changes, and current status of each PR. This log is designed to scale up to PR-120.

---

## PR-001: Initialize Monorepo

**Goal:** Establish the foundational monorepo structure for FlowBiz AI Core.

**Key Changes:**
- Created monorepo layout with `apps/api/` and `packages/core/`
- Set up `pyproject.toml` with project metadata and dependencies
- Added initial FastAPI application skeleton
- Configured basic project structure and build system

**Status:** ✅ Merged

---

## PR-002: Add Basic API Endpoints

**Goal:** Implement core API endpoints for health checks and metadata.

**Key Changes:**
- Added `/healthz` endpoint for health monitoring
- Added `/v1/meta` endpoint for service metadata
- Implemented `MetaService` in `packages/core/services/`
- Created router structure in `apps/api/routes/`

**Status:** ✅ Merged

---

## PR-003: Add Configuration Management

**Goal:** Centralize application settings and environment variable handling.

**Key Changes:**
- Implemented `AppSettings` class using Pydantic Settings
- Added `.env.example` with default configuration values
- Created `get_settings()` function with LRU caching
- Implemented custom `CommaSeparatedListEnvSource` for CORS settings
- Added support for comma-separated list parsing for configuration

**Status:** ✅ Merged

---

## PR-004: Add Structured Logging

**Goal:** Implement structured logging with request ID tracking.

**Key Changes:**
- Created `get_logger()` utility in `packages/core/logging.py`
- Implemented `RequestIdFormatter` for consistent log formatting
- Implemented `RequestIdFilter` for request ID propagation
- Added context-aware logging with `REQUEST_ID_CTX_VAR`
- Configured log level from environment variables

**Status:** ✅ Merged

---

## PR-005: Add Request ID Middleware

**Goal:** Enable request tracking across the application lifecycle.

**Key Changes:**
- Implemented `RequestIdMiddleware` to generate/validate request IDs
- Added `X-Request-ID` header handling (input and output)
- Used UUID4 for request ID generation
- Integrated with context variable for cross-cutting concerns

**Status:** ✅ Merged

---

## PR-006: Add Request Logging Middleware

**Goal:** Log all HTTP requests with duration and status tracking.

**Key Changes:**
- Implemented `RequestLoggingMiddleware` for automatic request logging
- Added timing measurement using `perf_counter`
- Logged method, path, status code, duration, and request ID
- Used appropriate log levels (INFO, WARNING, ERROR) based on status codes

**Status:** ✅ Merged

---

## PR-007: Add CORS Configuration

**Goal:** Enable cross-origin resource sharing with configurable policies.

**Key Changes:**
- Integrated FastAPI's `CORSMiddleware`
- Added CORS configuration options to `AppSettings`
- Supported configurable origins, methods, headers, and credentials
- Provided sensible defaults for local development

**Status:** ✅ Merged

---

## PR-008: Add Error Handling

**Goal:** Standardize error responses and exception handling.

**Key Changes:**
- Implemented `build_error_response()` utility in `packages/core/errors.py`
- Added exception handlers for HTTP exceptions, validation errors, and unhandled exceptions
- Ensured consistent error response format with request IDs
- Integrated error logging with appropriate log levels

**Status:** ✅ Merged

---

## PR-009: Add Version Information

**Goal:** Provide version and build metadata for the service.

**Key Changes:**
- Implemented `VersionInfo` dataclass in `packages/core/version.py`
- Added `get_version_info()` function reading from environment variables
- Supported `APP_VERSION`, `GIT_SHA`, and `BUILD_TIME` variables
- Integrated version info into metadata endpoints

**Status:** ✅ Merged

---

## PR-010: Add Docker Support

**Goal:** Containerize the application for consistent deployment.

**Key Changes:**
- Created multi-stage `Dockerfile` with builder and runtime stages
- Used Python 3.11-slim base image
- Implemented non-root user for security
- Built wheel distribution for efficient installation
- Exposed port 8000 and configured uvicorn startup

**Status:** ✅ Merged

---

## PR-011: Add PostgreSQL Integration

**Goal:** Integrate PostgreSQL database for persistence.

**Key Changes:**
- Added PostgreSQL service to `docker-compose.yml`
- Configured health check for database availability
- Added database URL configuration to `AppSettings`
- Set up volume for data persistence
- Configured dependency ordering (API depends on DB health)

**Status:** ✅ Merged

---

## PR-012: Add Docker Compose Orchestration

**Goal:** Orchestrate multi-service local development environment.

**Key Changes:**
- Created `docker-compose.yml` with API and DB services
- Configured service dependencies and health checks
- Added environment variable handling via `.env` file
- Set up named volume for PostgreSQL data persistence
- Documented local development workflow

**Status:** ✅ Merged

---

## PR-013: Add Nginx Reverse Proxy

**Goal:** Add production-grade reverse proxy for the API service.

**Key Changes:**
- Added Nginx service to `docker-compose.yml`
- Created `nginx/default.conf.template` with reverse proxy configuration
- Implemented dynamic DNS resolution for Docker services
- Added WebSocket support with connection upgrade handling
- Configured standard proxy headers (Host, X-Real-IP, X-Forwarded-For, X-Forwarded-Proto)
- Exposed port 80 for external access

**Status:** ✅ Merged

---

## PR-014: Add Foundation Documentation

**Goal:** Provide comprehensive documentation for architecture, deployment, and PR history.

**Key Changes:**
- Created `docs/PR_LOG.md` tracking PR-001 through PR-013
- Created `docs/ARCHITECTURE.md` documenting system design
- Created `docs/DEPLOYMENT_VPS.md` with VPS deployment guide
- Updated `README.md` with documentation links

**Status:** 🚧 In Progress

---

## PR-025: Tool Registry v2 (Skeleton, In-Memory, Contracts-First)

**Goal:** Create Tool Registry v2 as a minimal, deterministic, schema-first module for managing tool specifications and their lifecycle.

**Key Changes:**
- Added core contracts (`packages/core/contracts/tool_registry.py`): ToolSpec, ToolRegistration, ToolRegistrySnapshot
- Implemented ToolRegistryProtocol and ToolRegistryABC interfaces
- Implemented InMemoryToolRegistry with deterministic, sorted behavior
- Added comprehensive documentation (`docs/TOOL_REGISTRY.md`) with ADR on in-memory first approach
- Added 35 tests covering contracts, registration logic, enable/disable, and serialization
- All 182 tests pass with no regressions

**Status:** ✅ Ready for Review

---

## Future PRs (PR-015 to PR-120)

This section is reserved for future pull requests. Each PR should follow the same format:

**Template:**
```
## PR-XXX: [Title]

**Goal:** [Brief description of what this PR aims to achieve]

**Key Changes:**
- [Change 1]
- [Change 2]
- [Change 3]

**Status:** [🚧 In Progress | ✅ Merged | ❌ Closed]
```

---

## Status Legend

- ✅ **Merged**: PR has been reviewed, approved, and merged into main
- 🚧 **In Progress**: PR is currently being developed or reviewed
- ❌ **Closed**: PR was closed without merging
- 📝 **Draft**: PR is in draft state, not ready for review

---

## Notes

- All PRs should reference this log and update it as part of the changes
- Keep descriptions concise but informative
- Focus on "what" and "why" rather than implementation details
- Link to related issues or external documentation when relevant
