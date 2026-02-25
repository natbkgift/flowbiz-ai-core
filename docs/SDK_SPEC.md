# PR-048: Public SDK Specification (Docs-Only)

> **Scope:** Docs-only in flowbiz-ai-core. SDK generators and client libraries belong in separate repos.

## Overview

The FlowBiz AI Core public SDK defines how external consumers interact with the core API. SDK clients should be auto-generated from the OpenAPI specification.

## SDK Design Principles

1. **OpenAPI-first** — The OpenAPI schema (`/openapi.json`) is the single source of truth
2. **Language-agnostic** — SDK generators (openapi-generator, Kiota) produce clients for Python, TypeScript, Go, etc.
3. **Versioned** — SDK versions track API versions (v1, v2)
4. **Typed** — All request/response schemas use Pydantic models; SDK clients should preserve type safety

## SDK Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Health check |
| GET | `/v1/meta` | Service metadata |
| POST | `/v1/agent/run` | Execute an agent |
| GET | `/v1/agent/tools` | List registered tools |
| GET | `/v1/agent/health` | Agent subsystem health |
| GET | `/v2/meta` | Extended metadata (v2) |

## SDK Generation Workflow

```
1. Export OpenAPI schema: GET /openapi.json
2. Run generator: openapi-generator generate -i openapi.json -g python -o sdk/python
3. Validate SDK: run SDK test suite against local dev server
4. Publish: pip install / npm install
```

## Contract Types Available

Python consumers can also install `flowbiz-ai-core` directly and import contracts:

```python
from packages.core.contracts import (
    AgentResponseEnvelope,
    ToolResponseEnvelope,
    HealthResponse,
    RuntimeMeta,
)
```

## Next Steps (Separate Repos)

1. Set up OpenAPI generator CI pipeline
2. Create `flowbiz-sdk-python` repo
3. Create `flowbiz-sdk-typescript` repo
4. Add SDK integration tests
5. Publish to PyPI / npm
