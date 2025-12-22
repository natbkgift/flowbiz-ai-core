#!/usr/bin/env bash
set -euo pipefail

# shellcheck disable=SC2016

_read_from_github_event() {
    local key=$1
    if [[ -n "${GITHUB_EVENT_PATH:-}" && -f "${GITHUB_EVENT_PATH}" ]]; then
        python3 - "$GITHUB_EVENT_PATH" "$key" <<'PY'
import json
import sys

path, key = sys.argv[1], sys.argv[2]
with open(path, "r", encoding="utf-8") as event_file:
        event = json.load(event_file)

pr = event.get("pull_request") or {}
print(pr.get(key) or "")
PY
        return 0
    fi
    return 1
}

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

    _read_from_github_event "body" && return

  echo "No PR body available. Set PR_BODY, PR_BODY_PATH, or provide GITHUB_EVENT_PATH." >&2
  exit 1
}

read_pr_title() {
  if [[ -n "${PR_TITLE:-}" ]]; then
    printf '%s' "$PR_TITLE"
    return
  fi

    _read_from_github_event "title" && return

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
    ("summary", ["summary"]),
    ("scope", ["scope"]),
    (
        "in_scope_out_of_scope",
        [
            "in scope / out of scope",
            "in scope/out of scope",
            # legacy single heading accepted for backward compatibility
            "out of scope",
        ],
    ),
    ("files_changed", ["files changed"]),
    (
        "verification_testing",
        ["verification / testing", "verification/testing", "testing"],
    ),
    (
        "risk_rollback",
        [
            "risk & rollback",
            "risks & rollback",
            "risk and rollback",
            # legacy separate headings accepted
            "risks",
            "rollback",
        ],
    ),
]

command_keywords = ["pytest", "ruff", "docker compose", "curl"]

errors: list[str] = []
warnings: list[str] = []

if not body.strip():
    errors.append("PR description is required by Guardrails.")

all_heading_labels: list[str] = []
heading_to_key: dict[str, str] = {}
for key, labels in required_sections:
    for label in labels:
        normalized = label.lower()
        heading_to_key[normalized] = key
        all_heading_labels.append(normalized)

heading_union = "|".join(re.escape(label) for label in all_heading_labels)
heading_pattern = re.compile(rf"(?im)^\s*#{{1,3}}\s*({heading_union})\b.*$")

sections: dict[str, tuple[int, int]] = {}
for match in heading_pattern.finditer(body):
    label = match.group(1).lower()
    key = heading_to_key.get(label)
    if not key:
        continue
    sections.setdefault(key, (match.start(), match.end()))

sorted_sections = sorted(
    ((start, end, name) for name, (start, end) in sections.items()),
    key=lambda item: item[0],
)

section_bodies: dict[str, str] = {}
for idx, (heading_start, content_start, key) in enumerate(sorted_sections):
    end = len(body)
    if idx + 1 < len(sorted_sections):
        end = sorted_sections[idx + 1][0]
    section_bodies[key] = body[content_start:end].strip()

# Treat Files Changed as optional (warn only) to preserve legacy PRs
optional_keys = {"files_changed"}

for key, labels in required_sections:
    if key not in sections:
        if key in optional_keys:
            warnings.append(f"Missing optional section: ## {labels[0]}")
        else:
            errors.append(f"Missing section: ## {labels[0]}")
        continue

testing_key = "verification_testing"
if testing_key in section_bodies:
    testing_content = section_bodies.get(testing_key, "")
    lowered_testing = testing_content.lower()
    if not testing_content.strip():
        errors.append("Testing section present but empty.")
    else:
        has_keyword = any(keyword in lowered_testing for keyword in command_keywords)
        has_code = bool(re.search(r"`[^`]+`|```[\s\S]*?```", testing_content))
        if not (has_keyword or has_code):
            errors.append(
                "Testing section present but no commands detected (expected pytest/ruff/docker compose/curl or any code snippet)."
            )

# Accept either a checked checkbox or plain text acknowledgement; warn if missing
ack_pattern = re.compile(r"(?:-\s*\[[xX]\]\s*)?guardrails\s+followed", re.IGNORECASE)
if not ack_pattern.search(body):
    warnings.append("Missing acknowledgement: add '- [x] Guardrails followed' to PR body")

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
