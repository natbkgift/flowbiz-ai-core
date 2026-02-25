# Contributing to FlowBiz AI Core (PR-109)

## Start Here

Before opening a PR, read:
- `docs/SCOPE.md`
- `docs/GUARDRAILS.md`
- `docs/CODEX_PREFLIGHT.md`
- `docs/PR_LOG.md`
- `docs/PR_STATE.md`

## Core Scope Rules (Summary)

`flowbiz-ai-core` is for reusable core runtime primitives, contracts, schemas, and docs.

Do not add to this repo:
- UI/frontend implementations
- billing/payment logic
- platform-specific connectors/adapters
- client-specific business logic
- production deploy/infrastructure changes unless explicitly in scope

## Development Workflow

1. Create/choose the PR scope and persona (`core`, `infra`, `docs`)
2. Complete the pre-flight checklist in `docs/CODEX_PREFLIGHT.md`
3. Run baseline checks:
   - `ruff check .`
   - `pytest -q`
4. Implement only in scope
5. Re-run checks
6. Update `docs/PR_LOG.md` and `docs/PR_STATE.md`
7. Commit with `PR-XXX: <title>`

## Testing Expectations

- Functional changes must have tests (or clearly documented justification)
- Keep behavior deterministic in `packages/core` whenever possible
- Avoid external network/service dependencies in unit tests

## Documentation Expectations

- Update docs when behavior, contracts, or developer workflow changes
- Mark out-of-scope roadmap items as docs/contracts/stubs when applicable
- Make repo boundaries explicit when implementation belongs elsewhere

## Pull Request Hygiene

- Keep PRs focused and small
- List in-scope and out-of-scope areas
- Include testing commands/results
- Avoid unrelated refactors

## Questions / Unclear Scope

If unsure whether something belongs in core:
- stop and check `docs/SCOPE.md`
- prefer a docs-only proposal or contract stub
- document assumptions in the PR notes or PR description
