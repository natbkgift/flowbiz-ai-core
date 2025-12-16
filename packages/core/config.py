"""Configuration management for FlowBiz AI Core.

This module centralizes application settings and provides cached access
through :func:`get_settings`. Environment variables can be loaded from a
``.env`` file at the project root.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Iterable

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application settings sourced from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    env: str = Field(default="development", env="APP_ENV")
    name: str = Field(default="FlowBiz AI Core", env="APP_NAME")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    database_url: str = Field(default="postgresql://localhost:5432/flowbiz", env="DATABASE_URL")
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"], env="ALLOWED_ORIGINS")
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_allowed_origins(cls, value: str | Iterable[str]) -> list[str] | Iterable[str]:
        """Allow comma-separated origins in the environment variable."""

        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


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
