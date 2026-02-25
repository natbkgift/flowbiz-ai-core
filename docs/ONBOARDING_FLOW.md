# Onboarding Flow (PR-110)

## Purpose

Define a practical onboarding flow for contributors and agents working in `flowbiz-ai-core`.

## Audience

- New human contributors
- Automation agents operating in this repo
- Reviewers validating scope and guardrails compliance

## Onboarding Steps

1. Read repository boundaries and rules:
   - `docs/SCOPE.md`
   - `docs/GUARDRAILS.md`
   - `docs/CODEX_PREFLIGHT.md`
2. Review current roadmap state:
   - `docs/PR_LOG.md`
   - `docs/PR_STATE.md`
3. Set up local environment:
   - Python version supported by `pyproject.toml`
   - Install dev dependencies
4. Run baseline checks:
   - `ruff check .`
   - `pytest -q`
5. Select persona and lock scope for the next change
6. Record pre-flight answers in `docs/pr_notes/PR-XXX.md`
7. Implement only in-scope changes and re-run checks
8. Update PR tracking docs before commit

## Stop Conditions

Stop and ask for clarification when:
- scope crosses into UI/billing/platform integrations
- infra/deploy changes are required without explicit authorization
- credentials/secrets/external systems are needed

## Ownership Notes

- This doc defines process only
- UI onboarding flows (if any) belong in a web/docs platform repo, not core
