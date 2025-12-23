# Codex Pre-Flight Checklist

**MANDATORY: Complete this checklist BEFORE writing any code.** This is your essential pre-flight—short, strict, executable. Answer every item. Copy the template below into your PR description and fill it in.

---

## PR-021.2 — Codex Pre-flight (MUST ANSWER BEFORE CODE)

### Persona (pick one)
- [ ] persona:core
- [ ] persona:infra
- [ ] persona:docs

### Scope Lock 🔒
- **Goal (one sentence):** `<state your goal>`
- **In-scope files:** `<list specific files or patterns>`
- **Out-of-scope (3 bullets):**
  1. `<what you will NOT touch>`
  2. `<what you will NOT touch>`
  3. `<what you will NOT touch>`
- **Behavior changes:**
  - [ ] none
  - [ ] yes (describe): `<brief description>`

### Evidence (required)
- **PR description read:** [ ]
- **CI failures read (if any):** [ ]
- **Relevant logs / stack trace captured:** `<paste minimal excerpt or "N/A">`

### Plan (max 5 steps)
1. `<step 1>`
2. `<step 2>`
3. `<step 3>`
4. `<step 4>`
5. `<step 5>`

### Commands I will run locally
- [ ] `ruff check .`
- [ ] `pytest -q` (or `pytest tests/<specific> -q`)
- [ ] Any smoke command (if relevant): `<command or N/A>`

### Safety
- **New deps added?**
  - [ ] no
  - [ ] yes — list + reason: `<package names and why>`
- **Secrets/env touched?**
  - [ ] no
  - [ ] yes — explain: `<what and why>`

### Exit Criteria
- [ ] CI green on PR
- [ ] Summary + Testing filled in PR body
- [ ] No scope creep

---

## Why This Exists
This pre-flight locks your scope, forces evidence collection, and prevents scope creep. If you skip it, you risk:
- Working on the wrong thing
- Breaking unrelated code
- Violating guardrails
- CI red loops

**Agent Requirement:** If you're an AI agent, you MUST answer this checklist before making any code changes. No exceptions.

---

## Example (ready to copy)

```md
## 🧭 Codex Pre-Flight (Required)

### Persona (pick one)
- [x] persona:infra
- [ ] persona:core
- [ ] persona:docs

### Scope Lock 🔒
- **Goal (one sentence):** Make guardrails CI checks non-blocking and add PR comment bot
- **In-scope files:** `.github/workflows/*.yml`, `scripts/guardrails_pr_check.py`, `docs/GUARDRAILS.md`, `docs/CODEX_PREFLIGHT.md`
- **Out-of-scope (3 bullets):**
  1. No changes to runtime code in `apps/` or `packages/`
  2. No new dependencies or external tools
  3. No modifications to existing test files or logic
- **Behavior changes:**
  - [x] yes (describe): Guardrails checks will no longer fail CI; PR comment bot will post feedback instead

### Evidence (required)
- **PR description read:** [x]
- **CI failures read (if any):** [x] — Guardrails checks failing on recent PRs
- **Relevant logs / stack trace captured:** `Workflow logs show exit code 1 from guardrails_check.sh and pr-labels.yml`

### Plan (max 5 steps)
1. Create new `scripts/guardrails_pr_check.py` for detection (always exit 0)
2. Update `.github/workflows/guardrails.yml` to add PR comment bot job
3. Make `pr-labels.yml` and `ci.yml` guardrails jobs non-blocking
4. Update `docs/GUARDRAILS.md` to document non-blocking behavior
5. Update `docs/CODEX_PREFLIGHT.md` with killer format

### Commands I will run locally
- [x] `ruff check .`
- [x] `pytest -q`
- [ ] Any smoke command (if relevant): N/A — workflow syntax validated via GitHub Actions

### Safety
- **New deps added?**
  - [x] no
  - [ ] yes — list + reason: 
- **Secrets/env touched?**
  - [x] no
  - [ ] yes — explain: 

### Exit Criteria
- [x] CI green on PR
- [x] Summary + Testing filled in PR body
- [x] No scope creep
```

---

## Legacy Checklist (for reference only)

The original checklist format is preserved below for historical reference. New PRs should use the killer format above.

<details>
<summary>Click to expand legacy format</summary>

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
- PR: PR-123 — Add user authentication endpoint
- Type: Feature

### Scope
One-sentence scope: Add a new API endpoint for user login.

- [x] I can state the scope in one sentence
- [x] I listed files I expect to touch
- [x] I listed files I explicitly will NOT touch
- [x] I confirm no scope expansion without approval

- [x] I have read docs/GUARDRAILS.md
- [x] I am not changing app logic outside the stated scope
- [x] I am not adding dependencies without approval
- [x] I understand CI will fail if I violate Guardrails

What test(s) will prove this works? Guardrail docs updated; no runtime impact.

What command(s) will be run? `python -m pytest --maxfail=1`

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
</details>
