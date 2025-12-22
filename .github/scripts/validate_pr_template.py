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

# Default boilerplate content for template sections that should be replaced.
DEFAULT_SECTION_CONTENT = {
    "Summary": "-",
    "Scope": "-",
    "In Scope / Out of Scope": "- In scope:\n- Out of scope:",
    "Files Changed": "-",
    "Verification / Testing": (
        "- [ ] Not run (explain why)\n"
        "- [ ] Manual\n"
        "- [ ] Unit tests\n"
        "- [ ] Integration tests\n"
        "- [ ] Other (describe)"
    ),
    "Risk & Rollback": "- Risks:\n- Rollback plan:",
}


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


def has_meaningful_content(header: str, content: str) -> bool:
    """Return True when the section contains more than template placeholders."""

    if re.fullmatch(PLACEHOLDER_CONTENT_PATTERN, content):
        return False

    template_default = DEFAULT_SECTION_CONTENT.get(header)
    if template_default and content == template_default:
        return False

    lowered = content.lower()
    if header == "In Scope / Out of Scope":
        in_scope = re.search(r"-\s*in scope:\s*(.*)", lowered)
        out_scope = re.search(r"-\s*out of scope:\s*(.*)", lowered)
        in_scope_text = in_scope.group(1).strip() if in_scope else ""
        out_scope_text = out_scope.group(1).strip() if out_scope else ""
        return bool(in_scope_text or out_scope_text)

    if header == "Verification / Testing":
        has_checked_item = bool(re.search(r"-\s*\[x\]\s+", content, flags=re.IGNORECASE))
        return has_checked_item

    if header == "Risk & Rollback":
        risk_match = re.search(r"-\s*risks:\s*(.*)", lowered)
        rollback_match = re.search(r"-\s*rollback plan:\s*(.*)", lowered)
        risk_text = risk_match.group(1).strip() if risk_match else ""
        rollback_text = rollback_match.group(1).strip() if rollback_match else ""
        return bool(risk_text or rollback_text)

    return bool(re.search(r"\w", content))


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

        if not has_meaningful_content(header, cleaned):
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
