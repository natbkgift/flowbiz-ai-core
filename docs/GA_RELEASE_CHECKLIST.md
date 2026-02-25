# GA Release Checklist (PR-120)

## Status

Docs-only(out-of-scope) in `flowbiz-ai-core`.

This checklist documents GA readiness/release considerations only. It does **not** execute deployments or production changes.

## Release Preconditions (Documentation / Process)

- [ ] `docs/PR_LOG.md` is up to date
- [ ] `docs/PR_STATE.md` reflects current roadmap completion
- [ ] Scope/guardrails docs are current (`SCOPE`, `GUARDRAILS`, `CODEX_PREFLIGHT`)
- [ ] Breaking changes documented (if any)
- [ ] Migration notes exist for downstream platform/client repos (if needed)

## Quality Gates (Core)

- [ ] `ruff check .` passes
- [ ] `pytest -q` passes
- [ ] Contract/example docs updated for recent changes

## Platform/Release Steps (Outside Core Repo)

The following must happen in platform/infra repos or controlled deployment lanes:
- release tagging/versioning strategy
- build pipelines and artifact publishing
- deploy rollout/rollback
- production validation/monitoring
- incident response readiness

## Explicit Non-Goals of This PR

- No deploy execution
- No VPS/nginx mutation
- No secret management changes
- No platform UI changes

## Completion Note

PR-120 marks roadmap completion in this repo for the current practical numbering plan, with out-of-scope items represented as docs/contracts/stubs where required.
