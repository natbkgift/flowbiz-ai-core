# Guardrails

These guardrails define how FlowBiz AI Core is maintained. Guardrails are **non-blocking in CI** but enforced through **automated PR comments** and **pre-flight checklists**. Recommended rules guide contributors and agents.

## CI Enforcement (Non-blocking)
Guardrails checks run in GitHub Actions but **do not fail CI builds**. Instead:

- **Automated PR Comment Bot**: Posts or updates a single comment on your PR with:
  - Missing persona label (if any)
  - Missing or incomplete PR description sections (Summary, Testing)
  - Quick fix instructions with links
  
- **Pre-Flight Enforcement**: Before writing code, agents and contributors must complete the [Codex Pre-Flight Checklist](./CODEX_PREFLIGHT.md) which includes persona selection and scope lock.

The guardrails workflows live in:
- `.github/workflows/guardrails.yml` — Main PR comment bot + non-blocking checks
- `.github/workflows/pr-labels.yml` — Advisory persona label validation
- `.github/workflows/ci.yml` — Advisory PR template validation

All guardrails jobs are marked as `continue-on-error: true` or always exit with code 0, ensuring they never block CI.

### Why Non-blocking?
Guardrails hygiene shouldn't stop urgent fixes or block legitimate PRs. Instead:
- The **PR comment bot** provides immediate, actionable feedback
- The **pre-flight checklist** ensures planning happens before coding
- Reviewers can enforce guardrails during code review if needed

### PR Comment Bot
The bot runs on PR events (opened, edited, synchronize, labeled, unlabeled) and:
- Detects missing persona label and PR description sections
- Posts or updates a single comment (no spam) marked with `<!-- flowbiz-guardrails-bot -->`
- Shows ✅ when all checks pass or ⚠️ with remediation steps when items are missing

### Persona Label Requirement
Every PR should declare exactly one **persona label** so work is scoped and routed correctly:

- `persona:core` — Core domain logic and business rules
- `persona:infra` — Infrastructure, deployment, and operational changes
- `persona:docs` — Documentation updates

The bot will remind you if:
- No persona label exists
- More than one persona label exists

### PR Description Requirements
Your PR description should include (minimum):
- `## Summary` — Brief description of changes
- `## Testing` (or `## Verification / Testing`) — How you verified the changes

The full PR template also includes:
- `## Scope` — What parts of the system are affected
- `## In Scope / Out of Scope` — Clear boundaries
- `## Files Changed` — Important or risky files (optional)
- `## Risk & Rollback` — Risks and rollback plan

See `.github/pull_request_template.md` for the complete template.

## Pre-Flight Checklist (Required before coding)
Complete the Codex Pre-Flight checklist in `docs/CODEX_PREFLIGHT.md` **before writing any code**. Copy the template into the PR description and fill it out. CI checks for the final confirmation line (`- [x] Pre-Flight completed before writing code`) as evidence that the pre-flight was done.

## Enforced Rules (Hard Guardrails)
The following rules are non-negotiable. PRs that violate them should be rejected or fixed before merge.

- **No business logic in `apps/api/`.** The API layer may orchestrate calls, validate input/output, and map errors, but business rules belong in `packages/core` or other domain modules.
- **`packages/core` cannot depend on the API layer.** Core is the stable foundation and must stay free of FastAPI or transport concerns to avoid circular coupling.
- **Infrastructure files require explicit review.** Changes to `docker-compose*.yml`, `nginx/**`, and `.github/**` need the designated owners to approve because they impact delivery, security, and automation.
- **No silent behavior changes without tests.** Any functional change must include or update automated tests that demonstrate the new behavior.
- **No breaking changes without a version note.** When behavior changes incompatibly, add a clear note in release documentation or changelog so downstream users can plan upgrades.
- **PR template must be completed.** All required sections in `.github/pull_request_template.md` must be filled with meaningful content; CI enforces this.

## Architecture Boundaries and Responsibilities
These boundaries describe what each layer may and may not do. Each boundary includes the reason it exists.

- **API layer (`apps/api`)**
  - **Responsibilities:** HTTP concerns (routing, validation, error mapping), middleware registration, and request/response shaping.
  - **Must Not:** Implement domain or business rules; reach into infrastructure deployment config; own persistence concerns directly.
  - **Why:** Keeps transport logic thin and replaceable while preserving a clean domain surface.

- **Core domain (`packages/core`)**
  - **Responsibilities:** Business logic, domain services, validation that is not transport-specific, and shared utilities.
  - **Must Not:** Import from `apps/api` or any HTTP transport package; embed deployment specifics (ports, ingress); rely on request context.
  - **Why:** Preserves reusability across transports (CLI, workers) and prevents dependency cycles.

- **Infrastructure & deployment (e.g., `docker-compose*.yml`, `nginx/**`, CI workflows)**
  - **Responsibilities:** Runtime topology, networking, observability plumbing, and automation.
  - **Must Not:** Introduce business rules or mutate domain behavior without corresponding code/test changes; bypass required reviewers.
  - **Why:** Separates operational risk from product logic and ensures infra changes receive specialized review.

- **Cross-layer contracts**
  - **Data flows from API → Core, never the reverse.** Core exposes functions/services that API consumes.
  - **Error handling is standardized at the boundary.** Core returns structured errors; API translates to HTTP responses.
  - **Why:** Maintains a one-directional dependency graph and predictable error semantics.

---
## Core Boundaries (SCOPE)

FlowBiz AI Core has **strict scope boundaries** to keep the repository lean, stable, and transport-agnostic. These boundaries are documented in detail in [`docs/SCOPE.md`](./SCOPE.md).

**Key principle:** Core is for **reusable contracts, runtime primitives, and observability hooks**. It must not contain:
- UI/frontend code (Next.js, React, admin panels)
- Billing/payment logic (Stripe, subscriptions, invoicing)
- Platform-specific integrations (TikTok adapters, social media SDKs)
- Client-specific business logic
- Platform infrastructure (WAF, CDN, multi-tenant quota enforcement)

**PR requirement:** All PRs must respect scope boundaries. If a change touches UI, billing, platform integrations, or client-specific logic, it does not belong in core and should be rejected or moved to the appropriate repository (platform or client).

**If unsure:** Consult [`docs/SCOPE.md`](./SCOPE.md) or open an issue to discuss placement before submitting a PR.

---

## Recommended (Not Enforced) — Strongly Encouraged
These practices improve maintainability but can be waived with reviewer justification.

- Prefer pure, side-effect-light functions in `packages/core` to simplify testing and reuse.
- Keep PRs reasonably scoped (aim for ~400 LOC or less) to streamline reviews.
- Add or update tests whenever touching shared utilities or cross-cutting behaviors.
- Update relevant documentation when observable behavior changes.
- Use feature flags or configuration toggles for risky or incremental rollouts.
- Favor small, incremental migrations over large refactors without dedicated tracking.
