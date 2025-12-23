"""Tests for tool policy enforcement checker."""

from __future__ import annotations

import sys
from pathlib import Path

# Add scripts to path so we can import check_tools
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from check_tools import check_tool_file


def test_good_tool_passes_checks():
    """Test that a valid tool passes all policy checks."""
    good_tool_path = Path(__file__).parent / "test_tool_policy" / "test_good_tool.py"
    result = check_tool_file(good_tool_path)

    # Good tool should have no errors
    errors = [v for v in result.violations if v.severity == "error"]
    assert len(errors) == 0, f"Good tool should have no errors, found: {errors}"


def test_bad_tool_fails_checks():
    """Test that an invalid tool triggers policy violations."""
    bad_tool_path = Path(__file__).parent / "test_tool_policy" / "test_bad_tool.py"
    result = check_tool_file(bad_tool_path)

    # Bad tool should have errors
    errors = [v for v in result.violations if v.severity == "error"]
    assert len(errors) > 0, "Bad tool should have at least one error"

    # Check for specific expected violations
    error_rules = {v.rule for v in errors}
    assert "forbidden-import" in error_rules, "Should detect forbidden import"
    assert "forbidden-call" in error_rules, "Should detect forbidden call"
