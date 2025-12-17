import pytest

from packages.core.version import VersionInfo, get_version_info


@pytest.fixture(autouse=True)
def clear_version_env(monkeypatch: pytest.MonkeyPatch):
    """Ensure version-related environment variables do not leak between tests."""

    monkeypatch.delenv("APP_VERSION", raising=False)
    monkeypatch.delenv("GIT_SHA", raising=False)
    monkeypatch.delenv("BUILD_TIME", raising=False)
    yield
    monkeypatch.delenv("APP_VERSION", raising=False)
    monkeypatch.delenv("GIT_SHA", raising=False)
    monkeypatch.delenv("BUILD_TIME", raising=False)


def test_version_info_defaults():
    """Default values should be used when environment variables are absent."""

    version_info = get_version_info()

    assert version_info == VersionInfo(version="dev", git_sha="unknown", build_time=None)


def test_version_info_env_overrides(monkeypatch: pytest.MonkeyPatch):
    """Environment variables should override default version values."""

    monkeypatch.setenv("APP_VERSION", "1.0.0")
    monkeypatch.setenv("GIT_SHA", "abcdef1")
    monkeypatch.setenv("BUILD_TIME", "2024-01-01T00:00:00Z")

    version_info = get_version_info()

    assert version_info.version == "1.0.0"
    assert version_info.git_sha == "abcdef1"
    assert version_info.build_time == "2024-01-01T00:00:00Z"
