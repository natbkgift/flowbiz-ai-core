from __future__ import annotations

"""Provide service metadata lookups."""

from packages.core import get_settings, get_version_info


class MetaService:
    """Expose metadata about the running service."""

    def __init__(self) -> None:
        self._settings = get_settings()

    def get_meta(self) -> dict[str, str]:
        """Return service metadata including environment and version."""

        version_info = get_version_info()
        return {
            "service": self._settings.name,
            "env": self._settings.env,
            "version": version_info.version,
        }
