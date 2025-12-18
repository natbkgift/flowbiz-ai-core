import pytest

from packages.core.version import VersionInfo, get_version_info


@pytest.fixture(autouse=True)
def clear_version_env(monkeypatch: pytest.MonkeyPatch):
    """Ensure version-related environment variables do not leak between tests."""

    vars_to_clear = (
        "FLOWBIZ_VERSION",
        "FLOWBIZ_GIT_SHA",
        "FLOWBIZ_BUILD_TIME",
        "APP_VERSION",
        "GIT_SHA",
        "BUILD_TIME",
    )
    for var in vars_to_clear:
        monkeypatch.delenv(var, raising=False)
    yield
    for var in vars_to_clear:
        monkeypatch.delenv(var, raising=False)


def test_version_info_defaults():
    """Default values should be used when environment variables are absent."""

    version_info = get_version_info()

    assert version_info == VersionInfo(version="dev", git_sha="unknown", build_time=None)


def test_version_info_prefers_new_environment_variables(monkeypatch: pytest.MonkeyPatch):
    """New FLOWBIZ_* variables should override default version values."""

    monkeypatch.setenv("FLOWBIZ_VERSION", "1.0.0")
    monkeypatch.setenv("FLOWBIZ_GIT_SHA", "abcdef1")
    monkeypatch.setenv("FLOWBIZ_BUILD_TIME", "2024-01-01T00:00:00Z")

    version_info = get_version_info()

    assert version_info.version == "1.0.0"
    assert version_info.git_sha == "abcdef1"
    assert version_info.build_time == "2024-01-01T00:00:00Z"


def test_version_info_falls_back_to_legacy_variables(monkeypatch: pytest.MonkeyPatch):
    """Legacy APP_ variables should be used when new variables are absent."""

    monkeypatch.setenv("APP_VERSION", "0.9.0")
    monkeypatch.setenv("GIT_SHA", "1234567")
    monkeypatch.setenv("BUILD_TIME", "2023-12-31T23:59:59Z")

    version_info = get_version_info()

    assert version_info.version == "0.9.0"
    assert version_info.git_sha == "1234567"
    assert version_info.build_time == "2023-12-31T23:59:59Z"


def test_new_variables_take_precedence_over_legacy(monkeypatch: pytest.MonkeyPatch):
    """When both sets are present, FLOWBIZ_* variables should win."""

    monkeypatch.setenv("FLOWBIZ_VERSION", "2.0.0")
    monkeypatch.setenv("FLOWBIZ_GIT_SHA", "f00ba7")
    monkeypatch.setenv("FLOWBIZ_BUILD_TIME", "2025-01-01T00:00:00Z")
    monkeypatch.setenv("APP_VERSION", "1.0.0")
    monkeypatch.setenv("GIT_SHA", "abcdef1")
    monkeypatch.setenv("BUILD_TIME", "2024-01-01T00:00:00Z")

    version_info = get_version_info()

    assert version_info.version == "2.0.0"
    assert version_info.git_sha == "f00ba7"
    assert version_info.build_time == "2025-01-01T00:00:00Z"
