#!/usr/bin/env bash
set -euo pipefail

# shellcheck disable=SC2016

read_pr_body() {
  if [[ -n "${PR_BODY:-}" ]]; then
    printf '%s' "$PR_BODY"
    return
  fi

  if [[ -n "${PR_BODY_PATH:-}" ]]; then
    if [[ ! -f "$PR_BODY_PATH" ]]; then
      echo "PR_BODY_PATH is set but the file does not exist: $PR_BODY_PATH" >&2
      exit 1
    fi
    cat "$PR_BODY_PATH"
    return
  fi

  if [[ -n "${GITHUB_EVENT_PATH:-}" && -f "${GITHUB_EVENT_PATH}" ]]; then
    python3 - "$GITHUB_EVENT_PATH" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as event_file:
    event = json.load(event_file)

pr = event.get("pull_request") or {}
print(pr.get("body") or "")
PY
    return
  fi

  echo "No PR body available. Set PR_BODY, PR_BODY_PATH, or provide GITHUB_EVENT_PATH." >&2
  exit 1
}

read_pr_title() {
  if [[ -n "${PR_TITLE:-}" ]]; then
    printf '%s' "$PR_TITLE"
    return
  fi

  if [[ -n "${GITHUB_EVENT_PATH:-}" && -f "${GITHUB_EVENT_PATH}" ]]; then
    python3 - "$GITHUB_EVENT_PATH" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as event_file:
    event = json.load(event_file)

pr = event.get("pull_request") or {}
print(pr.get("title") or "")
PY
    return
  fi

  printf ''
}

main() {
  local body
  body="$(read_pr_body)"
  local title
  title="$(read_pr_title)"

  export PR_BODY_CONTENT="$body"
  export PR_TITLE_CONTENT="$title"

  python3 - <<'PY'
import os
import re
import sys

body = os.environ.get("PR_BODY_CONTENT", "")
title = os.environ.get("PR_TITLE_CONTENT", "")

required_sections = [
    ("summary", "## Summary"),
    ("scope", "## Scope"),
    ("out of scope", "## Out of scope"),
    ("testing", "## Testing"),
    ("risks", "## Risks"),
    ("rollback", "## Rollback"),
]

command_keywords = ["pytest", "ruff", "docker compose", "curl"]

errors: list[str] = []
warnings: list[str] = []

if not body.strip():
    errors.append("PR description is required by Guardrails.")

heading_pattern = re.compile(r"(?im)^\s*#{1,3}\s*(summary|scope|out of scope|testing|risks|rollback)\b.*$")

sections: dict[str, tuple[int, int]] = {}
for match in heading_pattern.finditer(body):
    name = match.group(1).lower()
    sections.setdefault(name, (match.start(), match.end()))

sorted_sections = sorted(
    ((start, end, name) for name, (start, end) in sections.items()),
    key=lambda item: item[0],
)

section_bodies: dict[str, str] = {}
for idx, (heading_start, content_start, name) in enumerate(sorted_sections):
    end = len(body)
    if idx + 1 < len(sorted_sections):
        end = sorted_sections[idx + 1][0]
    section_bodies[name] = body[content_start:end].strip()

for key, label in required_sections:
    if key not in sections:
        errors.append(f"Missing section: {label}")
        continue

if "testing" in section_bodies:
    testing_content = section_bodies.get("testing", "")
    lowered_testing = testing_content.lower()
    if not testing_content.strip():
        errors.append("Testing section present but empty.")
    elif not any(keyword in lowered_testing for keyword in command_keywords):
        errors.append(
            "Testing section present but no commands detected (expected pytest/ruff/docker compose/curl)."
        )

checkbox_pattern = re.compile(r"-\s*\[[xX]\]\s*guardrails\s+followed", re.IGNORECASE)
if not checkbox_pattern.search(body):
    errors.append("Missing acknowledgement checkbox: - [x] Guardrails followed")

if title:
    prefix_pattern = re.compile(r"^(PR|Chore|Feat|Fix|Docs|Refactor)[-: ]", re.IGNORECASE)
    if not prefix_pattern.search(title):
        warnings.append("PR title does not use a recognized prefix (e.g., PR-123: ...).")

if errors:
    print("Guardrails check failed:")
    for error in errors:
        print(f"- {error}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
    sys.exit(1)

print("Guardrails check passed: required sections, testing evidence, and acknowledgement are present.")
if warnings:
    print("Warnings:")
    for warning in warnings:
        print(f"- {warning}")
PY
}

main "$@"
