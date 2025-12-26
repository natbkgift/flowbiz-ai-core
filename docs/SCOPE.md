# FlowBiz AI Core — Scope & Boundaries

This document defines the **single source of truth** for what `flowbiz-ai-core` does and does not do. It establishes clear boundaries to prevent platform-specific code, UI components, billing logic, and client integrations from leaking into the core repository.

## TL;DR (30 seconds)
- Core = reusable contracts + runtime primitives + observability hooks
- Forbidden: UI, billing/payments, platform adapters, client-specific logic
- Folder boundaries define allowed/forbidden; follow intent over names
- Dependency direction is one-way: platform/clients → core
- Enforcement: This scope is enforced socially via [GUARDRAILS.md](./GUARDRAILS.md) (non-blocking)

---

## Purpose

**What `flowbiz-ai-core` is:**
- The **AI Core runtime + contracts + tooling foundation** for FlowBiz AI services
- A reusable, stable foundation that provides agent/tool interfaces, registries, schemas, and contracts
- The single place for deterministic utilities, observability hooks, and safety primitives used across FlowBiz AI systems

**Repository responsibility boundaries:**
- Core defines **contracts and interfaces** that platform and client projects depend on
- Core provides **runtime primitives** for agent execution and tool orchestration
- Core must remain **transport-agnostic** and **platform-independent**
- Core does **not** implement platform-specific features, UI layers, or business integrations

---

## What Core DOES (Allowed)

The following are **explicitly permitted** in `flowbiz-ai-core`:

- **Core runtime primitives:** Agent base classes, tool interfaces, execution context, result schemas
- **Agent/Tool registries:** Mechanisms to register, discover, and invoke agents and tools
- **Schemas and contracts:** Pydantic models for agent context, tool results, error responses, health checks, metadata
- **Deterministic utilities:** Pure functions for data transformation, validation, parsing
- **Observability hooks:** Trace ID generation, structured log schemas, request ID propagation
- **Safety hook contracts:** Abstract interfaces for safety checks (stub implementations allowed; enforcement logic belongs in platform)
- **Core HTTP API:** Minimal FastAPI app in `apps/api/` that exposes core functionality (health checks, metadata, agent execution endpoints)
- **Local development setup:** Docker Compose configuration for running core services locally
- **Core routing templates:** Basic nginx configurations for routing to core API (if present)
- **Shared error handling:** Standard error response formats and exception types
- **Configuration management:** Environment-based settings for core services
- **Testing infrastructure:** Unit and integration tests for core functionality

---

## What Core DOES NOT DO (Forbidden)

The following are **hard NO** items and must **never** appear in `flowbiz-ai-core`:

### UI/Frontend (Forbidden)
- ❌ Web UI frameworks (Next.js, Vite, React, Vue, Svelte)
- ❌ Frontend pages, components, or routes
- ❌ Public static assets for web UI
- ❌ Admin panels or dashboards
- ❌ Client-side JavaScript bundles

### Billing/Payments (Forbidden)
- ❌ Subscription management
- ❌ Payment processing (Stripe, PayPal integrations)
- ❌ Invoice generation
- ❌ Plan/quota enforcement at platform level
- ❌ Billing webhooks or APIs

### Platform-Specific Integrations (Forbidden)
- ❌ TikTok adapters, webhooks, or client SDK wrappers
- ❌ Social media platform-specific business logic (Instagram, YouTube, etc.)
- ❌ Third-party service adapters that are not core-agnostic (e.g., specialized CRM integrations)
- ❌ Client-specific webhooks or event handlers

### Platform Infrastructure (Forbidden)
- ❌ Multi-tenant plan/quota enforcement (belongs in platform layer)
- ❌ WAF/CDN configuration
- ❌ Production ingress routing (beyond basic core API routing)
- ❌ Platform-wide authentication dashboards
- ❌ System-level nginx vhosts for clients (those belong in VPS/system-nginx)
- ❌ Client-specific deployment configurations

### Client/Customer Code (Forbidden)
- ❌ Customer-specific business logic
- ❌ Per-client feature implementations
- ❌ Client project scaffolding (beyond templates/documentation)
- ❌ Custom workflows for individual customers

---

## Repo Boundaries (Folders & Ownership Rules)

The following table defines what is **allowed** and **forbidden** for each major area of the repository:

| Area | Allowed | Forbidden | Notes |
|------|---------|-----------|-------|
| `apps/api/` | Core HTTP API: health checks, metadata, agent execution endpoints. Middleware for logging, CORS, request IDs. | Client-specific endpoints, billing APIs, UI routes, platform-specific webhooks. | API layer orchestrates core primitives; no business logic. |
| `packages/core/` | Agent/tool base classes, registries, schemas, contracts, utilities, observability primitives, safety hook interfaces. | Platform adapters (TikTok, Stripe, etc.), UI components, client-specific logic, transport-specific code (FastAPI imports). | Core is the stable foundation; must be transport-agnostic. |
| `packages/core/agents/` | Agent base class, execution context, result schemas, default agent implementations. | Platform-specific agents (e.g., TikTokLiveAgent), client business logic. | Agents in core must be generic and reusable. |
| `packages/core/tools/` | Tool base class, authorization primitives, permission schemas, generic tool examples. | Platform-specific tools (e.g., TikTok API client), billing tools, UI-related tools. | Tools in core are contracts; integrations live elsewhere. |
| `packages/core/schemas/` | Request/response schemas, error schemas, health check models, metadata models. | Client-specific schemas, UI form schemas, billing models. | Schemas are contracts shared across layers. |
| `docs/` | Architecture, deployment guides, API documentation, guardrails, scope, ADRs, checklists. | Platform-specific runbooks, client project docs. | Docs are canonical guidance for core. |
| `nginx/` | Core routing templates for core API. | Client-specific vhosts, platform ingress rules, WAF configs. | Core nginx templates can be adapted by platform; client vhosts belong in system-nginx. |
| `tests/` | Unit and integration tests for core functionality. | Platform integration tests (unless mocked), client-specific tests. | Tests validate core contracts and behavior. |
| `scripts/` | Core utility scripts (guardrails checks, tooling setup). | Deployment automation for platform/clients, billing scripts. | Scripts support core development and CI. |

**Important:** If the folder structure evolves, apply these **rules by intent and responsibility**, not just by name. The principle is: **core = reusable contracts and runtime; platform/client = integrations and enforcement.**

---

## Interfaces / Contracts Policy

Core's primary role is to define **schemas and contract types** that platform and client projects depend on:

- **Core may define:** Abstract base classes, Pydantic schemas, type definitions, interface contracts
- **Core must not import:** Platform-specific code, client project modules, UI frameworks, billing integrations
- **Platform and clients may:** Import from core via version pinning (e.g., `pip install flowbiz-ai-core==1.2.3`)
- **Dependency direction:** Platform/clients → Core (one-way; never reversed)

**Version pinning and releases:**
- Core changes are versioned using semantic versioning
- Platform and client projects pin to specific core versions to avoid breakage
- Breaking changes in core require a major version bump and migration guide
- See future PR-024.2 for versioning and release process (not implemented in this PR)

---

## "If You're Unsure" Rule (Escalation)

When in doubt about whether a change belongs in core, follow this escalation process:

1. **Ask yourself:**
   - Is this a reusable contract/interface/utility, or is it platform/client-specific?
   - Does this change introduce a dependency on UI, billing, or platform integrations?
   - Would this code make sense in a CLI tool or background worker (transport-agnostic)?

2. **If any of the following apply, STOP:**
   - The change touches UI, billing, or payment logic
   - The change adds platform-specific adapters (TikTok, Stripe, etc.)
   - The change adds client-specific business rules
   - The change imports platform or client code into core
   - The change modifies production ingress/WAF/CDN config

3. **Instead:**
   - Open a **docs-only PR** proposing a design or ADR
   - Open an **issue** to discuss scope and placement
   - Consult `docs/SCOPE.md` (this document) and `docs/GUARDRAILS.md`
   - Consider creating the feature in platform/client repos instead

4. **For future consideration:**
   - If the change is borderline, propose an ADR (Architecture Decision Record) to document the reasoning
   - ADRs are not required for this PR but are recommended for major architectural decisions

---

## Examples (Allowed vs. Forbidden)

The following scenarios illustrate what is and is not allowed in `flowbiz-ai-core`:

### ✅ Allowed

1. **Add Pydantic schema for tool permissions**
   - File: `packages/core/schemas/tool_permission.py`
   - Reason: Defines a contract for tool authorization used across platform/clients

2. **Add abstract base class for agents**
   - File: `packages/core/agents/base.py`
   - Reason: Core runtime primitive; reusable across all projects

3. **Add generic tool interface documentation**
   - File: `docs/TOOLS.md`
   - Reason: Canonical guidance for how to implement tools

4. **Add health check endpoint**
   - File: `apps/api/routes/health.py`
   - Reason: Core HTTP API; simple health check endpoint

5. **Add trace ID middleware**
   - File: `apps/api/middleware.py`
   - Reason: Observability hook for request tracking

### ❌ Not Allowed

1. **Add TikTok webhook adapter**
   - Reason: Platform-specific integration; belongs in platform repo

2. **Add Stripe billing webhook handler**
   - Reason: Billing logic; belongs in platform billing service

3. **Add admin dashboard routes**
   - Reason: UI/frontend; belongs in platform UI repo

4. **Add client-specific business rule (e.g., "VIP customer gets 2x quota")**
   - Reason: Client-specific logic; belongs in client project or platform

5. **Add Next.js UI components**
   - Reason: Frontend framework; belongs in platform UI repo

6. **Add platform ingress rules with WAF config**
   - Reason: Platform infrastructure; belongs in platform deployment repo

---

## Enforcement

This document is **authoritative** but not automatically enforced by CI. Instead:

- **PR reviews** must check for scope violations
- **Guardrails bot** reminds contributors to respect scope (see `docs/GUARDRAILS.md`)
- **Pre-flight checklist** requires scope confirmation before coding (see `docs/CODEX_PREFLIGHT.md`)
- **ADRs** document borderline cases where scope is unclear

If a PR violates scope, reviewers should request changes or suggest moving the code to platform/client repos.

---

## Summary

- **Core = reusable contracts + runtime primitives + observability hooks**
- **Platform = integrations + enforcement + multi-tenancy + billing**
- **Clients = customer-specific business logic**

Keep core **lean, stable, and transport-agnostic**. Push platform-specific features, UI, billing, and client logic to their respective repos.

For questions or clarifications, open an issue or propose an ADR.
