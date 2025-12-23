#!/usr/bin/env python3
"""
Guardrails PR Check - Non-blocking detection script

This script detects missing guardrails items (persona labels, PR description sections)
and outputs results for use in CI and PR comment bot. Always exits with code 0.

Usage:
    python3 scripts/guardrails_pr_check.py

Environment variables:
    GITHUB_EVENT_PATH: Path to GitHub event JSON (optional, for PR context)
    PR_BODY: PR body text (optional, for testing)
    PR_LABELS: Comma-separated label names (optional, for testing)

Outputs to stdout in format:
    MISSING_PERSONA_LABEL=true/false
    MISSING_PR_DESCRIPTION=true/false
    DETAILS=<human readable details>
"""

import json
import os
import re
import sys
from typing import List, Tuple


def load_pr_data() -> Tuple[str, List[str]]:
    """Load PR body and labels from environment or GitHub event."""
    # Try direct env vars first (for testing)
    pr_body = os.environ.get("PR_BODY", "")
    pr_labels_str = os.environ.get("PR_LABELS", "")
    pr_labels = [label.strip() for label in pr_labels_str.split(",") if label.strip()] if pr_labels_str else []
    
    # If we have both from env, return them
    if pr_body and pr_labels:
        return pr_body, pr_labels
    
    # Otherwise try GitHub event path
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if event_path and os.path.exists(event_path):
        with open(event_path, "r", encoding="utf-8") as f:
            event = json.load(f)
        
        pr_data = event.get("pull_request", {})
        if not pr_body:
            pr_body = pr_data.get("body", "")
        if not pr_labels:
            pr_labels = [label["name"] for label in pr_data.get("labels", [])]
    
    return pr_body, pr_labels


def check_persona_label(labels: List[str]) -> Tuple[bool, str]:
    """
    Check if exactly one persona label exists.
    
    Returns:
        (missing, details) where missing=True if label is missing or multiple exist
    """
    allowed_labels = ["persona:core", "persona:infra", "persona:docs"]
    persona_labels = [label for label in labels if label in allowed_labels]
    
    if len(persona_labels) == 0:
        return True, "❌ Missing persona label. Add exactly one of: persona:core / persona:infra / persona:docs"
    elif len(persona_labels) > 1:
        return True, f"❌ Multiple persona labels found: {', '.join(persona_labels)}. Keep only one."
    else:
        return False, f"✅ Valid persona label: {persona_labels[0]}"


def check_pr_description(body: str) -> Tuple[bool, List[str]]:
    """
    Check if PR description contains required sections.
    
    Required sections (case-insensitive):
    - ## Summary
    - ## Testing (or ## Verification / Testing)
    
    Returns:
        (missing, issues) where missing=True if any required section is missing
    """
    issues = []
    
    if not body.strip():
        return True, ["❌ PR description is empty. Use the PR template."]
    
    # Check for Summary section
    summary_pattern = re.compile(r"^\s*#{1,3}\s*summary\b", re.IGNORECASE | re.MULTILINE)
    if not summary_pattern.search(body):
        issues.append("❌ Missing '## Summary' section")
    
    # Check for Testing section (accept multiple variants)
    testing_pattern = re.compile(
        r"^\s*#{1,3}\s*(testing|verification\s*/\s*testing|verification/testing)\b",
        re.IGNORECASE | re.MULTILINE
    )
    if not testing_pattern.search(body):
        issues.append("❌ Missing '## Testing' or '## Verification / Testing' section")
    
    if issues:
        return True, issues
    else:
        return False, ["✅ Required PR sections present"]


def main():
    """Main entry point - always exits with 0."""
    try:
        pr_body, pr_labels = load_pr_data()
        
        # Check persona label
        missing_persona, persona_details = check_persona_label(pr_labels)
        
        # Check PR description
        missing_description, description_issues = check_pr_description(pr_body)
        
        # Output results for GitHub Actions
        print(f"MISSING_PERSONA_LABEL={str(missing_persona).lower()}")
        print(f"MISSING_PR_DESCRIPTION={str(missing_description).lower()}")
        
        # Build details string
        details_lines = []
        details_lines.append(persona_details)
        details_lines.extend(description_issues)
        
        details = "\n".join(details_lines)
        print("DETAILS<<EOF")
        print(details)
        print("EOF")
        
        # Summary to stderr for visibility in logs
        if missing_persona or missing_description:
            print("\n⚠️  Guardrails Check Summary (Non-blocking):", file=sys.stderr)
            print(details, file=sys.stderr)
            print("\n💡 This check does not fail CI. See PR comment for remediation steps.", file=sys.stderr)
        else:
            print("\n✅ Guardrails Check Summary: All checks passed!", file=sys.stderr)
        
    except Exception as e:
        # Even on error, exit 0 (non-blocking)
        print(f"ERROR: {e}", file=sys.stderr)
        print("MISSING_PERSONA_LABEL=false")
        print("MISSING_PR_DESCRIPTION=false")
        print("DETAILS<<EOF")
        print(f"Error running guardrails check: {e}")
        print("EOF")
    
    # Always exit 0 (non-blocking)
    sys.exit(0)


if __name__ == "__main__":
    main()
