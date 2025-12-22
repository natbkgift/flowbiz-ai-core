import json
import os
import re
import sys
from typing import List, Dict, Tuple

# Backward-compatible heading groups: canonical header -> list of acceptable variants
HEADING_GROUPS: Dict[str, List[str]] = {
    "Summary": ["summary"],
    "Scope": ["scope"],
    # Accept combined or legacy single heading
    "In Scope / Out of Scope": [
        "in scope / out of scope",
        "in scope/out of scope",
        "out of scope",
    ],
    # Keep Files Changed as optional (non-blocking warning for legacy PRs)
    "Files Changed": ["files changed"],
    # Accept combined, plus legacy separate headings (handled specially below)
    "Verification / Testing": ["verification / testing", "verification/testing", "testing"],
    "Risk & Rollback": [
        "risk & rollback",
        "risks & rollback",
        "risk and rollback",
        # legacy separate headings (special handling below)
        "risks",
        "rollback",
    ],
}

# Headers that should not block CI if missing (emit warning only)
OPTIONAL_HEADERS = {"Files Changed"}

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


def _find_sections_by_variants(body: str, variants: List[str]) -> List[Tuple[str, str]]:
    """Find sections by any acceptable heading variants.

    Returns list of (matched_variant, content).
    Supports markdown heading levels #, ##, or ### (case-insensitive).
    """
    results: List[Tuple[str, str]] = []
    for v in variants:
        # Accept #, ## or ###, allow extra spaces, match until next heading
        pattern = rf"(?im)^\s*#{{1,3}}\s*{re.escape(v)}\s*(.*?)\s*(?=\n\s*#|\Z)"
        match = re.search(pattern, body, flags=re.DOTALL | re.IGNORECASE | re.MULTILINE)
        if match:
            results.append((v, match.group(1)))
    return results

def find_section(body: str, canonical_header: str) -> str:
    """Return content of the section for a canonical header using variants.

    Special handling:
      - Risk & Rollback: accept either a combined heading OR both separate
        'Risks' and 'Rollback' headings; concatenate their contents.
    """
    variants = HEADING_GROUPS.get(canonical_header, [canonical_header.lower()])
    found = _find_sections_by_variants(body, variants)
    if canonical_header == "Risk & Rollback":
        # If combined exists, prefer it
        for name, content in found:
            if name.lower() in {"risk & rollback", "risks & rollback", "risk and rollback"}:
                return content
        # Else, accept separate legacy headings if both present
        legacy_map = {name.lower(): content for name, content in found}
        if "risks" in legacy_map and "rollback" in legacy_map:
            return (legacy_map["risks"].strip() + "\n\n" + legacy_map["rollback"].strip()).strip()
        return ""

    # For In Scope / Out of Scope: if only legacy 'out of scope' present, accept it
    if canonical_header == "In Scope / Out of Scope":
        if found:
            # prefer combined if present
            for name, content in found:
                if name.lower() in {"in scope / out of scope", "in scope/out of scope"}:
                    return content
            # else return legacy 'out of scope' content
            return found[0][1]
        return ""

    # Default: return first match content if any
    return found[0][1] if found else ""


def _has_meaningful_subsection(content: str, subheadings: list[str]) -> bool:
    """Check if any subsection has meaningful content after its subheading.
    
    Args:
        content: The section content to check.
        subheadings: List of subsection names (e.g., ["in scope", "out of scope"]).
    
    Returns:
        True if at least one subsection has non-empty content.
    """
    lowered_content = content.lower()
    for sub in subheadings:
        # Pattern to find e.g., '- in scope: some content'
        pattern = rf"-\s*{re.escape(sub)}:\s*(.*)"
        match = re.search(pattern, lowered_content)
        if match and match.group(1).strip():
            return True
    return False


def has_meaningful_content(header: str, content: str) -> bool:
    """Return True when the section contains more than template placeholders."""

    if re.fullmatch(PLACEHOLDER_CONTENT_PATTERN, content):
        return False

    template_default = DEFAULT_SECTION_CONTENT.get(header)
    if template_default and content == template_default:
        return False

    if header == "In Scope / Out of Scope":
        return _has_meaningful_subsection(content, ["in scope", "out of scope"])

    if header == "Verification / Testing":
        has_checked_item = bool(re.search(r"-\s*\[x\]\s+", content, flags=re.IGNORECASE))
        return has_checked_item

    if header == "Risk & Rollback":
        return _has_meaningful_subsection(content, ["risks", "rollback plan"])

    return bool(re.search(r"\w", content))


def validate_sections(body: str) -> List[str]:
    errors: List[str] = []
    warnings: List[str] = []

    if not body.strip():
        errors.append("PR body is empty; fill out the pull request template.")
        return errors

    for header in HEADING_GROUPS.keys():
        content = find_section(body, header)
        if not content:
            if header in OPTIONAL_HEADERS:
                warnings.append(f"Missing optional section: {header}")
            else:
                errors.append(f"Missing required section: {header}")
            continue

        cleaned = content.strip()
        if not cleaned:
            errors.append(f"Section '{header}' must not be empty.")
            continue

        if not has_meaningful_content(header, cleaned):
            errors.append(f"Section '{header}' must include meaningful content.")

    # Emit warnings (non-blocking) for visibility
    for w in warnings:
        print(f"Warning: {w}")
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
