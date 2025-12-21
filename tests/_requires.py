"""Test requirement helpers."""

import importlib.util

import pytest


def has_httpx() -> bool:
    """Return True if httpx is installed."""

    return importlib.util.find_spec("httpx") is not None


requires_httpx = pytest.mark.skipif(
    not has_httpx(), reason="httpx is required for FastAPI TestClient tests"
)
