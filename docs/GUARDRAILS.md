# Guardrails

These guardrails define how FlowBiz AI Core is maintained. Enforced rules are blocking; recommended rules guide contributors and agents.

## CI Enforcement
Guardrails are enforced by GitHub Actions to stop PRs that do not follow the template. The workflow lives in `.github/workflows/guardrails.yml` and runs on pull requests (pushes to `main` are skipped). It fails when any of the following are missing from the PR description:

- Required headings (any Markdown level `#`, `##`, or `###`): `Summary`, `Scope`, `In Scope / Out of Scope`, `Files Changed`, `Verification / Testing`, and `Risk & Rollback`.
- Evidence of testing in the Testing section, which can be:
  - Test commands (e.g., `pytest`, `ruff`, `docker compose`, or `curl`)
  - Code snippets in backticks
  - Template checkboxes (e.g., `- [x] Manual`, `- [x] Unit tests`)
  - Testing descriptions (e.g., "Tested locally", "Manual testing", "Manually tested", "Verified", etc.)
- A checked acknowledgement line, such as `- [x] Guardrails followed`.

The workflow also emits a warning (non-blocking) if the PR title does not start with a recognizable prefix such as `PR-123:` or `Feat:`.

### Persona Label Requirement
Every PR must declare exactly one **persona label** so work is scoped and routed correctly. The workflow in `.github/workflows/pr-labels.yml` enforces this requirement and fails when:
- No persona label exists
- More than one persona label exists

Allowed persona labels:
- `persona:core` — Core domain logic and business rules
- `persona:infra` — Infrastructure, deployment, and operational changes
- `persona:docs` — Documentation updates

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

## Recommended (Not Enforced) — Strongly Encouraged
These practices improve maintainability but can be waived with reviewer justification.

- Prefer pure, side-effect-light functions in `packages/core` to simplify testing and reuse.
- Keep PRs reasonably scoped (aim for ~400 LOC or less) to streamline reviews.
- Add or update tests whenever touching shared utilities or cross-cutting behaviors.
- Update relevant documentation when observable behavior changes.
- Use feature flags or configuration toggles for risky or incremental rollouts.
- Favor small, incremental migrations over large refactors without dedicated tracking.
