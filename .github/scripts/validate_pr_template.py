import json
import os
import re
import sys
from typing import List

REQUIRED_HEADERS = [
    "Summary",
    "Scope",
    "In Scope / Out of Scope",
    "Files Changed",
    "Verification / Testing",
    "Risk & Rollback",
]

# Matches strings containing only whitespace, markdown list/task markers, and punctuation.
PLACEHOLDER_CONTENT_PATTERN = r"[-\s\[\]()*`'\"._,]*"


def load_pr_body() -> str:
    body_path = os.environ.get("PR_BODY_PATH")
    if body_path:
        if not os.path.exists(body_path):
            print(f"PR_BODY_PATH is set but file does not exist: {body_path}")
            sys.exit(1)

        with open(body_path, "r", encoding="utf-8") as body_file:
            return body_file.read()

    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not os.path.exists(event_path):
        print(
            "No PR body source found. Set PR_BODY_PATH for local runs or provide "
            "GITHUB_EVENT_PATH from the workflow event."
        )
        sys.exit(1)

    with open(event_path, "r", encoding="utf-8") as event_file:
        event = json.load(event_file)

    pr_data = event.get("pull_request") or {}
    body = pr_data.get("body")
    return body or ""


def find_section(body: str, header: str) -> str:
    pattern = rf"## {re.escape(header)}\s*(.*?)\s*(?=\n## |\Z)"
    match = re.search(pattern, body, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1) if match else ""


def validate_sections(body: str) -> List[str]:
    errors: List[str] = []

    if not body.strip():
        errors.append("PR body is empty; fill out the pull request template.")
        return errors

    for header in REQUIRED_HEADERS:
        content = find_section(body, header)
        if not content:
            errors.append(f"Missing required section: {header}")
            continue

        cleaned = content.strip()
        if not cleaned:
            errors.append(f"Section '{header}' must not be empty.")
            continue

        if re.fullmatch(PLACEHOLDER_CONTENT_PATTERN, cleaned):
            errors.append(f"Section '{header}' must include meaningful content.")

    return errors


def main() -> None:
    body = load_pr_body()
    errors = validate_sections(body)

    if errors:
        print("PR template validation failed:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)

    print("PR template validation passed: all required sections are present and non-empty.")


if __name__ == "__main__":
    main()
