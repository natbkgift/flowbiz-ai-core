from __future__ import annotations

"""Provide service metadata lookups."""

import os

from packages.core import get_settings


class MetaService:
    """Expose metadata about the running service."""

    def __init__(self) -> None:
        self._settings = get_settings()

    def get_meta(self) -> dict[str, str]:
        """Return service metadata including environment and version."""

        version = os.getenv("APP_VERSION") or "dev"
        return {"service": self._settings.name, "env": self._settings.env, "version": version}
