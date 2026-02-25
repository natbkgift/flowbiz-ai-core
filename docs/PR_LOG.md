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
- Created `docs/PR_LOG.md` tracking PR-001 through PR-013 (updated to include all PRs through PR-025)
- Created `docs/ARCHITECTURE.md` documenting system design (updated with runtime consolidation guidance)
- Created `docs/DEPLOYMENT_VPS.md` with VPS deployment guide
- Updated `README.md` with documentation links (enhanced with key new documentation)
- **Runtime Consolidation**: Clarified that the new runtime (`packages.core.runtime`) is recommended over the legacy runtime (`packages.core.agents`)

**Status:** ✅ Merged

---

## PR-022: Agent Runtime Skeleton with echo agent and /v1/agent/run endpoint

**Goal:** Implement minimal runtime plumbing for agent execution via HTTP.

**Key Changes:**
- Added `packages/core/runtime/` module with context, request/result schemas, agent base, and orchestrator
- Added `packages/core/runtime/agents/` with built-in echo agent
- Added `POST /v1/agent/run` endpoint (legacy moved to `/legacy`)
- Added comprehensive unit and integration test coverage (43 tests)
- Implemented deterministic echo agent for end-to-end validation

**Status:** ✅ Merged

---

## PR-023: Add tool base interface (ToolBase, ToolContext, ToolResult)

**Goal:** Introduce foundation contracts for tool execution in the AI Hub.

**Key Changes:**
- Added `packages/core/tools/` module with base abstractions
- Implemented abstract `ToolBase` interface requiring `name`, `description`, `run()`
- Added immutable `ToolContext` for inputs and structured `ToolResult`/`ToolError` for outputs
- Enabled safe, observable, schema-validated tool invocation
- Added comprehensive tests (13 tests covering inheritance, immutability, serialization)

**Status:** ✅ Merged

---

## PR-023.1: Add DummyTool example as reference implementation

**Goal:** Add DummyTool as canonical reference implementation of the ToolBase interface.

**Key Changes:**
- Added `packages/core/tools/examples/dummy.py` with DummyTool implementation
- Demonstrated correct usage of ToolContext, ToolResult, and explicit error handling
- Added comprehensive test suite (9 tests) for the example tool
- Provided template for future tool development

**Status:** ✅ Merged

---

## PR-023.2: Tool Authoring Guide (Docs)

**Goal:** Define canonical specification for writing Tools in FlowBiz AI Core.

**Key Changes:**
- Added `docs/TOOLS.md` as single source of truth for Tool interface and lifecycle
- Documented authoring rules, error design guidelines, and testing requirements
- Established "Tools don't think, Tools only do" principle
- Provided DummyTool as reference implementation template
- Added tool readiness checklist for pre-merge verification

**Status:** ✅ Merged

---

## PR-023.3: Add tool lint & policy enforcement (CI)

**Goal:** Add AST-based static analysis to enforce critical Tool authoring rules via CI.

**Key Changes:**
- Added `scripts/check_tools.py` for Tool policy checking
- Added `tool-policy` job to `.github/workflows/ci.yml`
- Enforced critical rules (inheritance, forbidden imports/calls, return types)
- Added test fixtures for valid/invalid tools
- Updated `docs/TOOLS.md` with enforcement documentation

**Status:** ✅ Merged

---

## PR-023.4: Tool permissions (design-only)

**Goal:** Design-only permission model for tools and agent personas.

**Key Changes:**
- Added `docs/TOOL_PERMISSIONS.md` with complete permission model specification
- Added `packages/core/tools/permissions.py` with immutable Pydantic types
- Defined 7 initial permissions and 3 MVP personas (core, infra, docs)
- Established deny-by-default, least-privilege framework
- Added comprehensive tests (21 tests) for schema validation

**Status:** ✅ Merged

---

## PR-023.5: Permission examples per tool (examples-only)

**Goal:** Add permission declaration examples and guidelines for tool authors.

**Key Changes:**
- Added `docs/TOOL_PERMISSION_EXAMPLES.md` with tool category → permission mapping
- Updated `packages/core/tools/examples/dummy.py` with `permissions` property
- Provided 8 runnable examples and 5 anti-patterns
- Established consistent patterns for declaring tool capabilities

**Status:** ✅ Merged

---

## PR-024.0: Scope + Boundaries (Docs-only)

**Goal:** Establish canonical scope boundaries for flowbiz-ai-core.

**Key Changes:**
- Added `docs/SCOPE.md` defining what belongs in core vs. platform/client repos
- Updated `docs/GUARDRAILS.md` with Core boundaries section
- Established folder-level ownership rules and dependency direction
- Defined forbidden items (UI, billing, TikTok adapters, platform infra)

**Status:** ✅ Merged

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

**Status:** ✅ Merged

---

## PR-024.1: Contract Package (schema-only)

**Goal:** Formalize and verify a schema-only contract package boundary for cross-repo data exchange.

**Key Changes:**
- Added contract package guidance at `docs/contracts/CONTRACT_PACKAGE.md`
- Added package-level tests in `tests/test_contract_package.py` to verify exports and schema invariants
- Verified contract models remain immutable (`frozen=True`) and reject unknown fields (`extra="forbid"`)
- Added Codex pre-flight note for traceability at `docs/pr_notes/PR-024.1.md`

**Status:** ✅ Merged

**Notes:** Schema-only package; no runtime integration behavior or deployment changes.

---

## PR-024.2: Version pinning & integration notes

**Goal:** Define practical version pinning policy and downstream integration guidance for consumers of `flowbiz-ai-core` contracts.

**Key Changes:**
- Added `docs/contracts/VERSION_PINNING_AND_INTEGRATION.md` with pinning policy and upgrade workflow
- Updated `docs/contracts/CONTRACT_PACKAGE.md` integration reference to point to the new guidance
- Linked contract version pinning guidance from `README.md`
- Added pre-flight trace note at `docs/pr_notes/PR-024.2.md`

**Status:** ✅ Merged

**Notes:** Docs-only PR; no runtime logic, infra, deploy, or integration execution changes.

---

## PR-024: Agent registry v2 (register/enable/disable)

**Goal:** Introduce deterministic Agent Registry v2 and wire runtime execution to registry lifecycle state.

**Key Changes:**
- Added schema-only contracts at `packages/core/contracts/agent_registry.py` (`AgentSpec`, `AgentRegistration`, `AgentRegistrySnapshot`)
- Added in-memory registry implementation at `packages/core/agent_registry.py` with register/list/get/set_enabled/remove
- Integrated registry checks into `packages/core/runtime/runtime.py` with runtime-level `enable_agent`/`disable_agent`
- Added tests at `tests/test_agent_registry.py` and expanded runtime tests for disable/reenable behavior

**Status:** ✅ Merged

**Notes:** In-scope core runtime enhancement; no infra/deploy/platform integration changes.

---

## PR-026: Response contract schemas (agent/tool envelopes + errors)

**Goal:** Add canonical schema-only response envelopes for agent/tool outputs with normalized error payloads.

**Key Changes:**
- Added `packages/core/contracts/response.py` with `ResponseError`, `AgentResponseEnvelope`, and `ToolResponseEnvelope`
- Exported new response contracts in `packages/core/contracts/__init__.py`
- Added contract tests in `tests/test_response_contracts.py`
- Updated contract export assertions in `tests/test_contract_package.py`

**Status:** ✅ Merged

**Notes:** Contract-first schema addition only; no API integration behavior change in this PR.

---

## PR-027: Observability hooks (trace_id + tool-call log schema)

**Goal:** Introduce contract-first observability hooks for trace context and tool-call logging.

**Key Changes:**
- Added observability contracts in `packages/core/contracts/observability.py` (`TraceContextContract`, `ToolCallLogEntry`)
- Added helper module `packages/core/observability.py` for deterministic log entry construction
- Exported observability contracts via `packages/core/contracts/__init__.py`
- Added tests in `tests/test_observability_hooks.py` and updated contract export assertions

**Status:** ✅ Merged

**Notes:** Core observability schema/hooks only; no external logging backend integration or deploy changes.

---

## PR-028: Safety gate hook (optional)

**Goal:** Add an optional safety gate hook contract and runtime pre-check integration with safe default behavior.

**Key Changes:**
- Added safety contracts in `packages/core/contracts/safety.py` (`SafetyDecision`, `SafetyGateInput`)
- Added safety hook abstraction in `packages/core/safety_gate.py` (`SafetyGateProtocol`, `AllowAllSafetyGate`)
- Integrated optional safety pre-check in `packages/core/runtime/runtime.py` before agent execution
- Added tests in `tests/test_safety_gate.py` and runtime deny-path coverage in `tests/test_runtime_unit.py`

**Status:** ✅ Merged

**Notes:** Core-only optional hook; no external moderation vendor or platform-specific policy integration.

---

## PR-028.1: LLM adapter abstraction

**Goal:** Add transport-agnostic LLM adapter contracts and a deterministic stub adapter for future provider integrations.

**Key Changes:**
- Added contracts in `packages/core/contracts/llm_adapter.py` (`LLMRequest`, `LLMResponse`, `LLMAdapterInfo`)
- Added adapter abstraction in `packages/core/llm_adapter.py` (`LLMAdapterProtocol`, `StubLLMAdapter`)
- Exported new contract symbols via `packages/core/contracts/__init__.py`
- Added tests in `tests/test_llm_adapter.py` and updated contract export assertions

**Status:** ✅ Merged

**Notes:** Contract/stub abstraction only; no external LLM SDK integration or secret handling.

---

## PR-028.2: Prompt template system

**Goal:** Introduce a deterministic prompt template registry and rendering contracts with strict variable validation.

**Key Changes:**
- Added prompt template contracts in `packages/core/contracts/prompt_template.py`
- Added `PromptTemplateRegistry` and rendering logic in `packages/core/prompt_templates.py`
- Exported new contract symbols via `packages/core/contracts/__init__.py`
- Added tests in `tests/test_prompt_templates.py` and updated contract export assertions

**Status:** ✅ Merged

**Notes:** Core-only template primitives; no provider/runtime orchestration integration in this PR.

---

## PR-028.3: Prompt versioning

**Goal:** Add deterministic prompt versioning support to template registration and rendering.

**Key Changes:**
- Extended prompt contracts in `packages/core/contracts/prompt_template.py` with version fields
- Upgraded `PromptTemplateRegistry` in `packages/core/prompt_templates.py` to store multiple versions per template
- Added latest-version fallback rendering and explicit-version rendering support
- Added tests for versioned behavior and sorted version listing in `tests/test_prompt_templates.py`

**Status:** ✅ Merged

**Notes:** Core versioning primitives only; no runtime/provider orchestration coupling.

---

## PR-029: Personas: core/infra/docs

**Goal:** Define persona contracts and an in-memory persona registry so agents can be tagged as core, infra, or docs persona types.

**Key Changes:**
- Added `packages/core/contracts/persona.py` with `PersonaType` literal, `PersonaSpec`, `PersonaAssignment`, and canonical constants (`CORE_PERSONA`, `INFRA_PERSONA`, `DOCS_PERSONA`, `ALL_PERSONAS`)
- Added `packages/core/persona_registry.py` with `PersonaRegistry` class (assign/get/list/filter/remove operations)
- Updated `packages/core/contracts/__init__.py` to export `PersonaSpec` and `PersonaAssignment`
- Updated `tests/test_contract_package.py` with new expected symbols
- Added comprehensive tests in `tests/test_persona.py` (15 tests covering contracts immutability, registry CRUD, filtering)

**Status:** ✅ Merged

**Notes:** Schema + registry primitives only; no routing or permission logic yet.

---

## PR-030: Routing rules v1 (rule-based intent router)

**Goal:** Implement a rule-based intent router that matches inbound intent strings to target personas/agents via keyword or regex pattern rules, evaluated in priority order.

**Key Changes:**
- Added `packages/core/contracts/routing.py` with `RoutingRule` (keyword/pattern strategy, priority, enabled flag) and `RoutingResult` schemas
- Added `packages/core/intent_router.py` with `IntentRouter` class (add/remove rules, route intent, priority-sorted evaluation)
- Updated `packages/core/contracts/__init__.py` to export `RoutingRule` and `RoutingResult`
- Updated `tests/test_contract_package.py` with new expected symbols
- Added 16 tests in `tests/test_intent_router.py` covering keyword/pattern matching, priority ordering, disabled rules, duplicates, and edge cases

**Status:** ✅ Merged

**Notes:** Rule-based routing primitives only; no LLM-based classification or middleware integration yet.

---

## PR-031: Tool permissions per persona (allowlist)

**Goal:** Implement runtime tool permission checking that ties persona-based `AgentPolicy` to tool `ToolPermissions` declarations, producing a `PolicyDecision`.

**Key Changes:**
- Added `packages/core/tool_permission_checker.py` with `check_tool_permission(policy, tool_perms, tool_name)` function
- Deny-first evaluation: tool allowlist → required permissions → allow
- Optional permissions do not block execution
- Added 12 tests in `tests/test_tool_permission_checker.py` covering allow/deny/ordering scenarios and persona integration examples

**Status:** ✅ Merged

**Notes:** Authorization checker only; not yet wired into execution pipeline.

---

## PR-032: Agent config loader (yaml/env)

**Goal:** Define agent configuration contracts and a loader that validates raw dicts (from YAML/JSON/env) into typed `AgentConfig` / `AgentConfigSet` models.

**Key Changes:**
- Added `packages/core/contracts/agent_config.py` with `AgentConfig` (name, persona, description, enabled, tags, allowed_tools) and `AgentConfigSet` schemas
- Added `packages/core/agent_config_loader.py` with `load_agent_config`, `load_agent_config_set`, `load_agent_configs_from_list` functions
- Updated contract exports and `test_contract_package.py`
- Added 14 tests in `tests/test_agent_config_loader.py`

**Status:** ✅ Merged

**Notes:** No file I/O or YAML parsing — caller provides raw dicts. Pure validation layer.

---

## PR-033: Docs Agent safe IO rules (no code exec)

**Goal:** Define canonical persona policies encoding least-privilege rules — docs agents can only read/write files, with no shell, network, or DB access.

**Key Changes:**
- Added `packages/core/persona_policies.py` with `DOCS_AGENT_POLICY`, `INFRA_AGENT_POLICY`, `CORE_AGENT_POLICY`, and `ALL_AGENT_POLICIES` dict
- Docs: READ_FS + WRITE_FS only. No EXEC_SHELL, NET_HTTP, DB_*, READ_ENV
- Infra: READ_FS + WRITE_FS + NET_HTTP + EXEC_SHELL + READ_ENV
- Core: READ_FS + NET_HTTP + READ_ENV
- Added 17 tests in `tests/test_persona_policies.py` verifying allow/deny per persona

**Status:** ✅ Merged

**Notes:** Policy constants only; not yet wired into runtime enforcement.

---

## PR-034: Infra Agent ops guardrails (compose/health/logs only)

**Goal:** Constrain infra agent shell commands to an allowlist of safe operations (compose, health checks, log viewing, system monitoring) with a deny-pattern blocklist for destructive commands.

**Key Changes:**
- Added `packages/core/ops_guardrail.py` with `OpsGuardrail` class and `OpsCommandResult` contract
- Default allowed prefixes: docker compose/ps/logs, curl, tail, journalctl, df/du/free/uptime, ping/dig/ss, systemctl status
- Deny patterns block: `rm -rf`, `mkfs`, `dd`, `shutdown/reboot/halt/poweroff`, `chmod 777`, writes to `/dev/`
- Word-boundary prefix matching prevents false positives (e.g., `ss` vs `ssh`)
- Added 44 tests in `tests/test_ops_guardrail.py`

**Status:** ✅ Merged

**Notes:** Guardrail checker only; not yet integrated into execution pipeline.

---

## PR-035: Execution pipeline v1 (steps, stop conditions)

**Goal:** Implement a contract-first execution pipeline with ordered steps, stop conditions, and handler registration.

**Key Changes:**
- Added `packages/core/contracts/pipeline.py` with `StepStatus`/`StopCondition` literals, `PipelineStep`, `StepResult`, `PipelineSpec`, `PipelineResult` schemas
- Added `packages/core/pipeline_runner.py` with `PipelineRunner` class (register_handler, run with stop conditions: on_error/on_success/always/never)
- Exported pipeline contracts via `packages/core/contracts/__init__.py`
- Added 15 tests in `tests/test_pipeline_runner.py` (6 contract + 9 runner)

**Status:** ✅ Merged

**Notes:** Core runtime primitive; no external orchestrator integration.

---

## PR-036: Short-term memory object (in-memory)

**Goal:** Provide a simple key-value memory store scoped to a session/run for passing data between pipeline steps.

**Key Changes:**
- Added `packages/core/short_term_memory.py` with `MemoryEntry`, `MemorySnapshot` contracts and `ShortTermMemory` class (set/get/delete/keys/snapshot/clear)
- Added 10 tests in `tests/test_short_term_memory.py`

**Status:** ✅ Merged

**Notes:** In-memory only; no persistence backend.

---

## PR-037: Conversation state schema (deterministic)

**Goal:** Define a deterministic, serialisable conversation state that tracks turns between user, agent, and system.

**Key Changes:**
- Added `packages/core/conversation.py` with `Role` literal, `ConversationTurn`, `ConversationState` contracts and `ConversationManager` class (add_turn/snapshot/clear)
- Added 8 tests in `tests/test_conversation.py`

**Status:** ✅ Merged

**Notes:** Schema + manager primitives; no persistence or transport coupling.

---

## PR-038: Retry/timeout/abort rules

**Goal:** Provide a configurable retry policy contract and executor with backoff and abort-on-exception support.

**Key Changes:**
- Added `packages/core/retry.py` with `RetryPolicy`, `RetryResult` contracts and `run_with_retry()` function
- Supports max retries, backoff seconds, and abort-on exception class names
- Added 7 tests in `tests/test_retry.py`

**Status:** ✅ Merged

**Notes:** Timeout is advisory; actual timeout mechanisms (threading) are left to callers.

---

## PR-039: Deterministic vs non-deterministic toggle

**Goal:** Provide an optional runtime flag controlling deterministic (reproducible) vs non-deterministic (creative) execution mode.

**Key Changes:**
- Added `packages/core/execution_mode.py` with `ExecutionMode` contract, `DETERMINISTIC_MODE`/`CREATIVE_MODE` constants, and `resolve_mode()` function
- Added 7 tests in `tests/test_execution_mode.py`

**Status:** ✅ Merged

**Notes:** Optional contract — agents may ignore the mode hint.

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
