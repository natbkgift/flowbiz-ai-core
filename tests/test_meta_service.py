import pytest

from packages.core import reset_settings_cache
from packages.core.services import MetaService


@pytest.fixture(autouse=True)
def reset_settings(monkeypatch: pytest.MonkeyPatch):
    """Ensure settings cache and related env are clean between tests."""

    reset_settings_cache()
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("APP_VERSION", raising=False)
    yield
    reset_settings_cache()


def test_meta_service_returns_settings(monkeypatch: pytest.MonkeyPatch):
    """MetaService should surface configured service name and environment."""

    monkeypatch.setenv("APP_NAME", "Meta Test Service")
    monkeypatch.setenv("APP_ENV", "staging")
    reset_settings_cache()

    service = MetaService()
    meta = service.get_meta()

    assert meta["service"] == "Meta Test Service"
    assert meta["env"] == "staging"


def test_meta_service_version_default(monkeypatch: pytest.MonkeyPatch):
    """Default version should be used when APP_VERSION is not set."""

    monkeypatch.delenv("APP_VERSION", raising=False)
    service = MetaService()

    assert service.get_meta()["version"] == "dev"


def test_meta_service_version_override(monkeypatch: pytest.MonkeyPatch):
    """Version should reflect APP_VERSION environment variable."""

    monkeypatch.setenv("APP_VERSION", "9.9.9")
    service = MetaService()

    assert service.get_meta()["version"] == "9.9.9"
