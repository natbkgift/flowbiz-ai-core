from packages.core import get_settings, reset_settings_cache


def teardown_function():
    reset_settings_cache()


def test_get_settings_returns_defaults(monkeypatch):
    reset_settings_cache()
    settings = get_settings()

    assert settings.env == "development"
    assert settings.name == "FlowBiz AI Core"
    assert settings.log_level == "INFO"
    assert settings.database_url == "postgresql://localhost:5432/flowbiz"
    assert settings.cors_allow_origins == ["http://localhost:3000"]
    assert settings.cors_allow_methods == ["*"]
    assert settings.cors_allow_headers == ["*"]
    assert settings.cors_allow_credentials is False
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8000


def test_get_settings_reads_environment(monkeypatch):
    reset_settings_cache()
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("APP_NAME", "Custom Name")
    monkeypatch.setenv("APP_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("APP_DATABASE_URL", "postgresql://db:5432/custom")
    monkeypatch.setenv("APP_CORS_ALLOW_ORIGINS", "https://example.com, http://localhost:3000")
    monkeypatch.setenv("APP_CORS_ALLOW_METHODS", "GET,POST")
    monkeypatch.setenv("APP_CORS_ALLOW_HEADERS", "Content-Type,Authorization")
    monkeypatch.setenv("APP_CORS_ALLOW_CREDENTIALS", "true")
    monkeypatch.setenv("APP_API_HOST", "127.0.0.1")
    monkeypatch.setenv("APP_API_PORT", "9000")

    settings = get_settings()

    assert settings.env == "staging"
    assert settings.name == "Custom Name"
    assert settings.log_level == "DEBUG"
    assert settings.database_url == "postgresql://db:5432/custom"
    assert settings.cors_allow_origins == ["https://example.com", "http://localhost:3000"]
    assert settings.cors_allow_methods == ["GET", "POST"]
    assert settings.cors_allow_headers == ["Content-Type", "Authorization"]
    assert settings.cors_allow_credentials is True
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 9000


def test_reset_settings_cache_reloads_environment(monkeypatch):
    reset_settings_cache()
    initial = get_settings()

    monkeypatch.setenv("APP_NAME", "After Cache")

    cached = get_settings()
    assert cached.name == initial.name

    reset_settings_cache()
    refreshed = get_settings()
    assert refreshed.name == "After Cache"
