"""Configuration management for FlowBiz AI Core.

This module centralizes application settings and provides cached access
through :func:`get_settings`. Environment variables can be loaded from a
``.env`` file at the project root.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, ClassVar

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, SettingsError
from pydantic_settings.sources import DotEnvSettingsSource, EnvSettingsSource


class CommaSeparatedListMixin:
    """Mixin to handle comma-separated lists for settings sources."""

    _list_fields = {
        "cors_allow_origins",
        "cors_allow_methods",
        "cors_allow_headers",
    }

    def prepare_field_value(
        self, field_name: str, field, value: Any, value_is_complex: bool
    ) -> Any:
        """Override to handle comma-separated lists specially."""
        if field_name in self._list_fields and isinstance(value, str):
            # Return the raw string for list fields, skip the parent's JSON parsing
            # The field_validator will handle the string-to-list conversion
            return value
        # For other fields, use the parent implementation
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class CommaSeparatedListSettingsSource(CommaSeparatedListMixin, EnvSettingsSource):
    """Custom env source that handles comma-separated lists without requiring JSON."""


class CommaSeparatedListDotEnvSource(CommaSeparatedListMixin, DotEnvSettingsSource):
    """Custom dotenv source that handles comma-separated lists without requiring JSON."""


class StrictEnvValidationMixin:
    """Raise an error when unexpected APP_* environment variables are present."""

    def _expected_env_keys(self) -> set[str]:
        return {
            env_name
            for field_name, field in self.settings_cls.model_fields.items()
            for _, env_name, _ in self._extract_field_info(field, field_name)
        }

    def _validate_unknown_env_vars(self) -> None:
        if not getattr(self, "env_prefix", None):
            return

        prefix = self.env_prefix.upper()
        allowed_keys = {key.upper() for key in self._expected_env_keys()}.union(
            key.upper() for key in getattr(self.settings_cls, "allowed_unknown_env_keys", set())
        )
        unexpected_keys = {
            key
            for key in self.env_vars.keys()
            if key.upper().startswith(prefix) and key.upper() not in allowed_keys
        }

        if unexpected_keys:
            message = ", ".join(sorted(unexpected_keys))
            raise SettingsError(f"Unexpected environment variables for {self.settings_cls.__name__}: {message}")


class StrictEnvSettingsSource(StrictEnvValidationMixin, CommaSeparatedListSettingsSource):
    """Env source that enforces known APP_* keys before parsing."""

    def __call__(self) -> dict[str, Any]:
        self._validate_unknown_env_vars()
        return super().__call__()


class StrictDotEnvSettingsSource(StrictEnvValidationMixin, CommaSeparatedListDotEnvSource):
    """Dotenv source that enforces known APP_* keys before parsing."""

    def __call__(self) -> dict[str, Any]:
        self._validate_unknown_env_vars()
        return super().__call__()


class AppSettings(BaseSettings):
    """Application settings sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="forbid",
    )

    # Environment keys prefixed with APP_ that should be tolerated even if not
    # defined as model fields. This allows utilities such as version providers
    # to read their own variables without breaking strict validation.
    allowed_unknown_env_keys: ClassVar[set[str]] = {
        "APP_VERSION",
        "APP_GIT_SHA",
        "APP_BUILD_TIME",
    }

    env: str = Field(default="development")
    name: str = Field(default="FlowBiz AI Core")
    log_level: str = Field(default="INFO")
    database_url: str = Field(default="postgresql://localhost:5432/flowbiz")
    cors_allow_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    cors_allow_methods: list[str] = Field(default_factory=lambda: ["*"])
    cors_allow_headers: list[str] = Field(default_factory=lambda: ["*"])
    cors_allow_credentials: bool = Field(default=False)
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)

    @field_validator(
        "cors_allow_origins", "cors_allow_methods", "cors_allow_headers", mode="before"
    )
    @classmethod
    def parse_comma_separated_lists(cls, value: Any) -> Any:
        """Parse comma-separated string values into lists."""
        if value is None:
            return ["*"]

        if isinstance(value, str):
            parsed = [item.strip() for item in value.split(",") if item.strip()]
            return parsed or ["*"]

        if isinstance(value, (list, tuple, set)):
            parsed = [item for item in value if str(item).strip()]
            return parsed or ["*"]

        return value

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        """Customize settings sources to use our custom env source."""
        return (
            init_settings,
            StrictEnvSettingsSource(settings_cls),
            StrictDotEnvSettingsSource(settings_cls),
            file_secret_settings,
        )


@lru_cache
def get_settings() -> AppSettings:
    """Return cached application settings instance."""

    return AppSettings()


def reset_settings_cache() -> None:
    """Clear the settings cache so new environment values are read.

    Intended for testing scenarios where environment variables change
    between assertions.
    """

    get_settings.cache_clear()
