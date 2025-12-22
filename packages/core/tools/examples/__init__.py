"""Example tools for reference and testing.

This module contains example-only tools that demonstrate proper
Tool interface implementation. These tools are NOT for production use.

Example tools serve as:
- Templates for creating new tools
- Test fixtures for Tool Registry
- Examples for Agent Runtime integration
"""

from __future__ import annotations

from .dummy import DummyTool

__all__ = ["DummyTool"]
