"""Version information provider for the service."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class VersionInfo:
    """Holds version and build metadata for the service."""

    version: str
    git_sha: str
    build_time: str | None = None


def get_version_info() -> VersionInfo:
    """Return version information resolved from the environment."""

    return VersionInfo(
        version=os.getenv("APP_VERSION") or "dev",
        git_sha=os.getenv("GIT_SHA") or "unknown",
        build_time=os.getenv("BUILD_TIME"),
    )
