# Codex Pre-Flight Checklist

Complete this checklist **before writing any code**. Answer with **Yes / No / N/A** and a brief justification where indicated. Keep the tone firm, calm, and professional. Copy the template below into your PR description and fill it in.

## Checklist Template (required)

### 1) Identity & Intent
- Role: Core / Infra / Docs / Mixed
- PR: PR-XXX — title
- Type: Bugfix / Feature / Refactor / Docs-only / Infra-only

### 2) Scope Lock 🔒 (MANDATORY)
One-sentence scope:

- [ ] I can state the scope in one sentence
- [ ] I listed files I expect to touch
- [ ] I listed files I explicitly will NOT touch
- [ ] I confirm no scope expansion without approval

### 3) Guardrails Acknowledgement
- [ ] I have read docs/GUARDRAILS.md
- [ ] I am not changing app logic outside the stated scope
- [ ] I am not adding dependencies without approval
- [ ] I understand CI will fail if I violate Guardrails

### 4) Tests & Verification Plan 🧪
What test(s) will prove this works?

What command(s) will be run?

- [ ] Existing tests cover this
- [ ] I will add tests
- [ ] Manual verification only (explain why)

### 5) Risk & Rollback
What could break?

Is rollback trivial? (yes/no)

Rollback command or action:

### 6) STOP Conditions 🛑
- [ ] If requirements are unclear, I will STOP and ask
- [ ] If scope expands, I will STOP and ask
- [ ] If CI rules block me, I will NOT bypass them

### 7) Final Pre-Flight Confirmation
- [ ] Pre-Flight completed before writing code

## Recommended Usage
- Complete this checklist even for small PRs to prevent scope creep.
- Keep it at the top of your PR description for reviewer transparency.

## Example (ready to copy)
```md
## 🧭 Codex Pre-Flight (Required)

- Role: Core
- PR: PR-123 — Add user authentication endpoint
- Type: Feature

### Scope
One-sentence scope: Add a new `/login` endpoint for user authentication with JWT token support.

- [x] I can state the scope in one sentence
- [x] I listed files I expect to touch (`apps/api/routes/auth.py`, `packages/core/auth/jwt.py`, `tests/test_auth.py`)
- [x] I listed files I explicitly will NOT touch (`packages/billing/`, `docker-compose.yml`, `apps/worker/`)
- [x] I confirm no scope expansion without approval

- [x] I have read docs/GUARDRAILS.md
- [x] I am not changing app logic outside the stated scope
- [x] I am not adding dependencies without approval
- [x] I understand CI will fail if I violate Guardrails

What test(s) will prove this works? Integration tests for `/login` endpoint, including success and failure cases.

What command(s) will be run? `pytest tests/test_auth.py -v` and `ruff check apps/api/routes/auth.py packages/core/auth/`

- [ ] Existing tests cover this
- [x] I will add tests
- [ ] Manual verification only (explain why)

What could break? Login flow if JWT signing fails; existing auth middleware may need updates.

Is rollback trivial? yes

Rollback command or action: git revert <commit>

- [x] If requirements are unclear, I will STOP and ask
- [x] If scope expands, I will STOP and ask
- [x] If CI rules block me, I will NOT bypass them

- [x] Pre-Flight completed before writing code
```
