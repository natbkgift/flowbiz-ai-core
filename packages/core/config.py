"""Configuration management for FlowBiz AI Core.

This module centralizes application settings and provides cached access
through :func:`get_settings`. Environment variables can be loaded from a
``.env`` file at the project root.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Iterable

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import EnvSettingsSource


class CommaSeparatedListEnvSource(EnvSettingsSource):
    """Custom env source that handles comma-separated lists without requiring JSON."""

    def prepare_field_value(
        self, field_name: str, field, value: Any, value_is_complex: bool
    ) -> Any:
        """Override to handle comma-separated lists specially."""
        if field_name == "allowed_origins" and isinstance(value, str):
            # Return the raw string for allowed_origins, skip the parent's JSON parsing
            # The field_validator will handle the string-to-list conversion
            return value
        # For other fields, use the parent implementation
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class AppSettings(BaseSettings):
    """Application settings sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_"
    )

    env: str = Field(default="development")
    name: str = Field(default="FlowBiz AI Core")
    log_level: str = Field(default="INFO")
    database_url: str = Field(default="postgresql://localhost:5432/flowbiz")
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: Any) -> Any:
        """Parse comma-separated string to list."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, (list, tuple, set)):
            return list(value)
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
            CommaSeparatedListEnvSource(settings_cls),
            dotenv_settings,
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
