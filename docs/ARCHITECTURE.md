# Architecture Documentation

This document describes the system architecture of FlowBiz AI Core, including its layers, data flow, configuration, logging, versioning, and infrastructure.

---

## Table of Contents

1. [Overview](#overview)
2. [System Layers](#system-layers)
3. [Data Flow](#data-flow)
4. [Configuration Management](#configuration-management)
5. [Logging System](#logging-system)
6. [Versioning Approach](#versioning-approach)
7. [Infrastructure](#infrastructure)

---

## Overview

FlowBiz AI Core is the foundational service layer for flowbiz.cloud, built as a Python monorepo using FastAPI. The architecture follows a layered approach with clear separation between the API layer and shared core utilities.

**Key Characteristics:**
- **Monorepo structure** for code sharing and consistency
- **FastAPI framework** for high-performance async API development
- **Pydantic** for configuration and data validation
- **Docker-based** deployment with container orchestration
- **Structured logging** with request tracking
- **Production-ready** with middleware, error handling, and health checks

---

## System Layers

The system is organized into three primary layers:

### 1. API Layer (`apps/api/`)

The API layer is the entry point for all HTTP requests. It contains:

**Components:**
- **`main.py`**: Application factory and FastAPI app configuration
  - Lifespan management for startup/shutdown hooks
  - Middleware registration (CORS, RequestId, RequestLogging)
  - Exception handler registration
  - Router inclusion

- **`middleware.py`**: Custom middleware implementations
  - `RequestIdMiddleware`: Generates/validates request IDs, adds X-Request-ID header
  - `RequestLoggingMiddleware`: Logs every request with method, path, status, duration

- **`routes/`**: API endpoint definitions
  - `health.py`: Health check endpoint (`/healthz`)
  - `v1/meta.py`: Versioned metadata endpoint (`/v1/meta`)

**Responsibilities:**
- Handle HTTP request/response lifecycle
- Route requests to appropriate handlers
- Apply cross-cutting concerns (logging, CORS, request IDs)
- Standardize error responses
- Validate request/response data

### 2. Core Layer (`packages/core/`)

The core layer provides shared utilities and domain logic used across the application.

**Components:**
- **`config.py`**: Centralized configuration management
  - `AppSettings`: Pydantic settings model
  - `get_settings()`: Cached settings accessor
  - `CommaSeparatedListEnvSource`: Custom environment variable parser

- **`logging.py`**: Structured logging infrastructure
  - `get_logger()`: Logger factory with structured formatting
  - `RequestIdFormatter`: Formats logs with request IDs
  - `RequestIdFilter`: Propagates request IDs to log records
  - `REQUEST_ID_CTX_VAR`: Context variable for request tracking

- **`errors.py`**: Error response utilities
  - `build_error_response()`: Creates standardized error payloads

- **`version.py`**: Version information provider
  - `VersionInfo`: Dataclass for version metadata
  - `get_version_info()`: Reads version from environment

- **`services/`**: Business logic and domain services
  - `meta_service.py`: Provides service metadata

**Responsibilities:**
- Provide reusable utilities
- Manage application configuration
- Implement domain logic
- Abstract infrastructure concerns

### 3. Infrastructure Layer

The infrastructure layer handles deployment, orchestration, and external dependencies.

**Components:**
- Docker containerization
- Docker Compose orchestration
- Nginx reverse proxy
- PostgreSQL database

---

## Data Flow

### Request Lifecycle

1. **Nginx Reception**
   - Request arrives at Nginx (port 80)
   - Nginx acts as reverse proxy, forwarding to API service (port 8000)
   - Headers added: `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`
   - WebSocket upgrade support enabled

2. **Middleware Chain (Outermost → Innermost)**
   
   **a. RequestIdMiddleware (Outermost)**
   - Extracts or generates request ID from `X-Request-ID` header
   - Validates UUID format, generates new UUID4 if invalid/missing
   - Stores request ID in context variable (`REQUEST_ID_CTX_VAR`)
   - Adds `X-Request-ID` to response headers
   
   **b. CORSMiddleware (Middle)**
   - Validates origin against allowed origins
   - Adds CORS headers to response
   - Handles preflight OPTIONS requests
   
   **c. RequestLoggingMiddleware (Innermost)**
   - Captures request start time
   - Allows request to proceed through application
   - Logs completed request with method, path, status, duration
   - Uses appropriate log level based on status code

3. **Router → Handler**
   - FastAPI routes request to appropriate handler function
   - Request validation (path params, query params, body)
   - Handler executes business logic
   - Response serialization

4. **Exception Handling**
   - HTTP exceptions → standardized error response with appropriate status
   - Validation errors → 422 response with error details
   - Unhandled exceptions → 500 response with generic message
   - All errors logged with request ID

5. **Response Return**
   - Middleware chain unwinds (innermost → outermost)
   - Headers added by each middleware
   - Response logged by `RequestLoggingMiddleware`
   - Request ID added to response by `RequestIdMiddleware`
   - Nginx forwards response to client

### Middleware Stack Visualization

```
┌─────────────────────────────────────┐
│           Nginx (Port 80)           │
│      Reverse Proxy + WebSocket      │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│       API Container (Port 8000)     │
│                                     │
│  ┌───────────────────────────────┐ │
│  │   RequestIdMiddleware         │ │ ◄── Outermost
│  │   (Generate/Validate UUID)    │ │
│  └──────────────┬────────────────┘ │
│                 │                   │
│  ┌──────────────▼────────────────┐ │
│  │      CORSMiddleware           │ │ ◄── Middle
│  │   (Cross-Origin Handling)     │ │
│  └──────────────┬────────────────┘ │
│                 │                   │
│  ┌──────────────▼────────────────┐ │
│  │  RequestLoggingMiddleware     │ │ ◄── Innermost
│  │   (Request Duration Logging)  │ │
│  └──────────────┬────────────────┘ │
│                 │                   │
│  ┌──────────────▼────────────────┐ │
│  │      FastAPI Routers          │ │
│  │    (Handler Functions)        │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## Configuration Management

### Environment Variables

Configuration is managed through environment variables with the `APP_` prefix. Variables are loaded from `.env` file or system environment. Version metadata now prefers the `FLOWBIZ_` prefix while continuing to fall back to the legacy `APP_` variables for compatibility.

**Key Configuration Options:**

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Environment name |
| `APP_NAME` | `FlowBiz AI Core` | Application name |
| `FLOWBIZ_VERSION` | `0.1.0` | Application version (falls back to `APP_VERSION`) |
| `FLOWBIZ_GIT_SHA` | `local-dev` | Git commit SHA (falls back to `GIT_SHA`) |
| `FLOWBIZ_BUILD_TIME` | `-` | Optional build timestamp (falls back to `BUILD_TIME`) |
| `APP_LOG_LEVEL` | `INFO` | Logging level |
| `APP_DATABASE_URL` | `postgresql://localhost:5432/flowbiz` | Database connection string |
| `APP_CORS_ALLOW_ORIGINS` | `http://localhost:3000` | Allowed CORS origins (comma-separated) |
| `APP_CORS_ALLOW_METHODS` | `GET,POST,PUT,PATCH,DELETE` | Allowed HTTP methods |
| `APP_CORS_ALLOW_HEADERS` | `Content-Type,Authorization` | Allowed headers |
| `APP_CORS_ALLOW_CREDENTIALS` | `false` | Allow credentials |
| `APP_API_HOST` | `0.0.0.0` | API bind host |
| `APP_API_PORT` | `8000` | API bind port |

### Settings Implementation

**`AppSettings` Class:**
- Uses Pydantic Settings for validation and parsing
- Implements `CommaSeparatedListEnvSource` for CORS list handling
- Provides type safety and validation
- Cached via `@lru_cache` on `get_settings()` for performance

**Access Pattern:**
```python
from packages.core import get_settings

settings = get_settings()
origins = settings.cors_allow_origins  # Returns list[str]
```

---

## Logging System

### Structured Logging

All logs follow a structured format with consistent fields:

**Log Format:**
```
%(asctime)s | %(levelname)s | %(message)s | request_id=%(request_id)s
```

**Example Output:**
```
2024-01-15 10:30:45,123 | INFO | request completed | request_id=a1b2c3d4-e5f6-4789-0abc-def123456789
```

### Components

**1. `get_logger(name: str)`**
- Factory function returning configured logger instance
- Thread-safe with double-checked locking
- Configures handler, formatter, and filter
- Sets log level from `APP_LOG_LEVEL` environment variable

**2. `RequestIdFormatter`**
- Ensures `request_id` attribute exists on log records
- Formats logs according to `LOG_FORMAT`
- Provides default "-" if request ID is missing

**3. `RequestIdFilter`**
- Attaches request ID from context variable to log record
- Ensures every log record has `request_id` attribute
- Handles pytest caplog compatibility

**4. `REQUEST_ID_CTX_VAR`**
- Context variable storing current request ID
- Set by `RequestIdMiddleware`
- Accessible throughout request lifecycle
- Automatically cleaned up after request completes

### Log Levels

Logs are emitted at appropriate levels based on context:

- **INFO**: Successful requests (2xx, 3xx status codes)
- **WARNING**: Client errors (4xx status codes)
- **ERROR**: Server errors (5xx status codes), unhandled exceptions
- **DEBUG**: Detailed diagnostic information (when `APP_LOG_LEVEL=DEBUG`)

### Request Logging

Every HTTP request is automatically logged with:
- HTTP method
- Request path
- Status code
- Duration in milliseconds
- Request ID

---

## Versioning Approach

### Version Information

Version metadata is sourced from environment variables and exposed via API. The preferred variables use the `FLOWBIZ_` prefix, with legacy `APP_` variables supported as fallbacks for compatibility:

**Environment Variables:**
- `FLOWBIZ_VERSION` (falls back to `APP_VERSION`): Application version (e.g., "0.1.0")
- `FLOWBIZ_GIT_SHA` (falls back to `GIT_SHA`): Git commit hash for traceability
- `FLOWBIZ_BUILD_TIME` (falls back to `BUILD_TIME`): ISO 8601 timestamp of build (optional)

**API Endpoints:**
- `/healthz`: Returns status, service name, and version
- `/v1/meta`: Returns complete version metadata

**Implementation:**
```python
@dataclass(frozen=True)
class VersionInfo:
    version: str
    git_sha: str
    build_time: str | None = None

def get_version_info() -> VersionInfo:
    return VersionInfo(
        version=os.getenv("FLOWBIZ_VERSION") or os.getenv("APP_VERSION") or "dev",
        git_sha=os.getenv("FLOWBIZ_GIT_SHA") or os.getenv("GIT_SHA") or "unknown",
        build_time=os.getenv("FLOWBIZ_BUILD_TIME") or os.getenv("BUILD_TIME"),
    )
```

### API Versioning

API endpoints are versioned using URL prefixes:
- `/v1/meta` - Version 1 metadata endpoint
- Future versions: `/v2/...`, `/v3/...`

This approach allows backward compatibility while introducing new API versions.

---

## Infrastructure

### Docker Containerization

**Multi-Stage Build:**
1. **Builder Stage**: Builds Python wheel distributions
   - Base: `python:3.11-slim`
   - Installs build dependencies
   - Creates wheels for project and dependencies

2. **Runtime Stage**: Minimal production image
   - Base: `python:3.11-slim`
   - Installs wheels from builder stage
   - Runs as non-root user (`app:app`)
   - Exposes port 8000
   - Entrypoint: `uvicorn apps.api.main:app --host 0.0.0.0 --port 8000`

**Image Characteristics:**
- Small footprint (slim base + wheel installation)
- Security: Non-root user execution
- Performance: Pre-built wheels, no runtime compilation
- Reproducibility: Locked dependencies via wheels

### Docker Compose Orchestration

**Services:**

1. **`nginx`** (Port 80)
   - Image: `nginx:1.25-alpine`
   - Reverse proxy to API service
   - Mounts: `nginx/templates/default.conf.template` for environment-based templating
   - Health check: `curl -f http://localhost/healthz`
   - Depends on: `api`

2. **`api`** (Port 8000, internal)
   - Build: Local Dockerfile
   - Environment: Loaded from `.env` file
   - Depends on: `db` (waits for healthy status)
   - Not directly exposed, accessed via nginx

3. **`db`** (Port 5432, internal)
   - Image: `postgres:16-alpine`
   - Environment: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
   - Volume: `postgres-data` for persistence
   - Health check: `pg_isready -U $POSTGRES_USER`

**Volumes:**
- `postgres-data`: Named volume for PostgreSQL data persistence

**Service Dependencies:**
- `nginx` → `api`: Nginx starts after API is ready
- `api` → `db`: API waits for DB to be healthy

### Nginx Configuration

**Key Features:**
- Dynamic DNS resolution using Docker's embedded DNS resolver (127.0.0.11 is Docker's internal DNS service)
- Upstream variable `$upstream_api` pointing to `api:8000`
- WebSocket support with connection upgrade handling
- Standard proxy headers forwarding

**Headers Set:**
- `Host`: Original host header
- `X-Real-IP`: Client IP address
- `X-Forwarded-For`: Proxy chain
- `X-Forwarded-Proto`: Original protocol (http/https)

**WebSocket Support:**
```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection $connection_upgrade;
```

### Network Architecture

```
┌──────────────────────────────────────────────────┐
│                   Host System                    │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │         Docker Compose Network             │ │
│  │                                            │ │
│  │  ┌──────────┐      ┌──────────┐          │ │
│  │  │  Nginx   │─────▶│   API    │          │ │
│  │  │  :80     │      │  :8000   │          │ │
│  │  └────┬─────┘      └────┬─────┘          │ │
│  │       │                 │                 │ │
│  │       │                 ▼                 │ │
│  │       │           ┌──────────┐           │ │
│  │       │           │ Postgres │           │ │
│  │       │           │  :5432   │           │ │
│  │       │           └──────────┘           │ │
│  │       │                 │                 │ │
│  │       │                 ▼                 │ │
│  │       │           [Volume: postgres-data] │ │
│  └───────┼─────────────────────────────────────┘
│          │                                     │
│     Port Mapping                               │
│     80:80 (Exposed)                            │
└──────────────────────────────────────────────────┘
```

**Access Patterns:**
- External → `http://localhost:80` → Nginx → API
- API → `postgresql://db:5432/flowbiz` → PostgreSQL

---

## Security Considerations

### Current Implementation

1. **Non-root container execution**: API runs as non-privileged `app` user
2. **Request ID tracking**: All requests traced for audit purposes
3. **Structured logging**: Security events logged with context
4. **Error masking**: Unhandled exceptions return generic 500 responses
5. **CORS enforcement**: Cross-origin requests restricted by configuration
6. **Health checks**: Automated monitoring of service availability

### Future Enhancements

- Authentication and authorization
- Rate limiting
- Input sanitization and validation
- HTTPS/TLS termination
- Secret management (e.g., HashiCorp Vault)
- Database connection pooling
- SQL injection prevention (via ORM)

---

## Development Workflow

### Local Development (Native Python)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .[dev]

# Configure environment
cp .env.example .env

# Run development server
uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest
```

### Local Development (Docker Compose)

```bash
# Configure environment
cp .env.example .env

# Start all services
docker compose up --build -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Testing Endpoints

```bash
# Health check
curl http://localhost:80/healthz

# Metadata
curl http://localhost:80/v1/meta

# Root endpoint
curl http://localhost:80/
```

---

## Monitoring and Observability

### Current Capabilities

1. **Health Checks**
   - `/healthz` endpoint returns service status
   - Docker health checks for automated restarts
   - Service name and version included

2. **Request Tracing**
   - Every request assigned unique UUID
   - Request ID propagated through logs
   - `X-Request-ID` header in responses

3. **Structured Logs**
   - Machine-readable log format
   - Request duration tracking
   - Status code tracking
   - Consistent log levels

### Future Enhancements

- Metrics export (Prometheus)
- Distributed tracing (OpenTelemetry)
- Log aggregation (ELK stack, Grafana Loki)
- Performance monitoring (APM)
- Alerting (PagerDuty, Opsgenie)

---

## Scalability Considerations

### Current Architecture

- **Stateless API**: No session state, enabling horizontal scaling
- **Health checks**: Support for load balancer integration
- **Request ID**: Enables request tracking across multiple instances
- **Docker-based**: Easy replication and orchestration

### Scaling Strategies

1. **Horizontal Scaling**: Run multiple API containers behind load balancer
2. **Database Scaling**: Connection pooling, read replicas, partitioning
3. **Caching**: Redis for session data and frequently accessed content
4. **CDN**: Static asset delivery
5. **Async Processing**: Task queues (Celery, RQ) for background jobs

---

## Summary

FlowBiz AI Core implements a clean, layered architecture with:
- **Clear separation** between API and core logic
- **Production-ready** middleware and error handling
- **Observable** via structured logging and request tracing
- **Containerized** for consistent deployment
- **Configurable** through environment variables
- **Scalable** stateless design

This foundation supports future enhancements while maintaining simplicity and reliability.
