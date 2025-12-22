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

What command(s) will be run? (Include real commands with recognizable tools such as `pytest`, `ruff`, `docker compose`, or `curl` so CI can validate this section.)

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
- PR: PR-021.2 — Add Codex pre-flight checklist
- Type: Docs-only

### Scope
One-sentence scope: Add Codex pre-flight checklist documentation only.

- [x] I can state the scope in one sentence
- [x] I listed files I expect to touch
- [x] I listed files I explicitly will NOT touch
- [x] I confirm no scope expansion without approval

- [x] I have read docs/GUARDRAILS.md
- [x] I am not changing app logic outside the stated scope
- [x] I am not adding dependencies without approval
- [x] I understand CI will fail if I violate Guardrails

What test(s) will prove this works? Guardrail docs updated; no runtime impact.

What command(s) will be run? `python -m pytest --maxfail=1` (include recognizable tools so CI can detect commands)

- [x] Existing tests cover this
- [ ] I will add tests
- [ ] Manual verification only (explain why)

What could break? None — documentation only.

Is rollback trivial? yes

Rollback command or action: git revert <commit>

- [x] If requirements are unclear, I will STOP and ask
- [x] If scope expands, I will STOP and ask
- [x] If CI rules block me, I will NOT bypass them

- [x] Pre-Flight completed before writing code
```
