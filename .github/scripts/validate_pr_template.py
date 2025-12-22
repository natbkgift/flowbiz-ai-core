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


def load_pr_body() -> str:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not os.path.exists(event_path):
        raise FileNotFoundError("GITHUB_EVENT_PATH is missing or does not exist; cannot validate PR body.")

    with open(event_path, "r", encoding="utf-8") as event_file:
        event = json.load(event_file)

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

        if re.fullmatch(r"[-\s\[\]()*`'\"._,]*", cleaned):
            errors.append(f"Section '{header}' must include meaningful content.")

    return errors


def main() -> None:
    try:
        body = load_pr_body()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    errors = validate_sections(body)

    if errors:
        print("PR template validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        sys.exit(1)

    print("PR template validation passed: all required sections are present and non-empty.")


if __name__ == "__main__":
    main()
