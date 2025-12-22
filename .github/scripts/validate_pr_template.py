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
PLACEHOLDER_CONTENT_PATTERN = r"[-\s\[\]()*`'\"#._,>|~]*"


def load_pr_body() -> str:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not os.path.exists(event_path):
        print("GITHUB_EVENT_PATH is missing; cannot validate PR body.")
        sys.exit(1)

    try:
        with open(event_path, "r", encoding="utf-8") as event_file:
            event = json.load(event_file)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {event_path}.")
        sys.exit(1)

    body = event.get("pull_request", {}).get("body")
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
