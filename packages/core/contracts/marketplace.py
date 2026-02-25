"""Agent marketplace contracts — PR-071 to PR-080.

Defines agent/tool manifests, versioning, sandboxing, permission
isolation, marketplace API contracts, rating, install/update,
and usage analytics.  Most marketplace UI/API lives outside core;
this module provides **contracts and stubs**.

PR-071: Agent manifest
PR-072: Tool manifest
PR-073: Agent versioning
PR-074: Agent sandbox
PR-075: Permission isolation
PR-076: Marketplace API (contracts only)
PR-077: Agent rating
PR-078: Agent install/update
PR-079: Agent usage analytics
PR-080: Marketplace UI API (docs-only — UI forbidden)
"""

from __future__ import annotations

import time
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# PR-071 — Agent manifest
# ---------------------------------------------------------------------------

AgentCategory = Literal[
    "general",
    "customer_support",
    "data_analysis",
    "content_creation",
    "automation",
    "integration",
]


class AgentManifest(BaseModel):
    """Declarative agent manifest for marketplace listing."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str
    name: str
    version: str
    description: str = ""
    author: str = ""
    category: AgentCategory = "general"
    tags: tuple[str, ...] = ()
    entry_point: str = ""  # module path
    required_tools: tuple[str, ...] = ()
    required_permissions: tuple[str, ...] = ()
    config_schema: dict[str, Any] = Field(default_factory=dict)
    min_core_version: str = "0.1.0"


# ---------------------------------------------------------------------------
# PR-072 — Tool manifest
# ---------------------------------------------------------------------------

ToolCategory = Literal[
    "api",
    "database",
    "file_system",
    "communication",
    "analytics",
    "utility",
]


class ToolManifest(BaseModel):
    """Declarative tool manifest for marketplace listing."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tool_id: str
    name: str
    version: str
    description: str = ""
    author: str = ""
    category: ToolCategory = "utility"
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    required_permissions: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# PR-073 — Agent versioning
# ---------------------------------------------------------------------------

VersionStatus = Literal["draft", "published", "deprecated", "archived"]


class AgentVersion(BaseModel):
    """Versioned release of an agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str
    version: str
    status: VersionStatus = "draft"
    changelog: str = ""
    published_at: float | None = None
    created_at: float = Field(default_factory=time.time)


# ---------------------------------------------------------------------------
# PR-074 — Agent sandbox
# ---------------------------------------------------------------------------

SandboxStatus = Literal["running", "stopped", "error"]


class SandboxConfig(BaseModel):
    """Configuration for agent sandboxed execution."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str
    memory_limit_mb: int = 256
    cpu_limit_millicores: int = 500
    timeout_seconds: int = 30
    network_access: bool = False
    allowed_tools: tuple[str, ...] = ()


class SandboxState(BaseModel):
    """Runtime state of a sandboxed agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str
    status: SandboxStatus = "stopped"
    uptime_seconds: float = 0.0
    memory_used_mb: float = 0.0
    invocation_count: int = 0


# ---------------------------------------------------------------------------
# PR-075 — Permission isolation
# ---------------------------------------------------------------------------

IsolationLevel = Literal["none", "basic", "strict"]


class PermissionBoundary(BaseModel):
    """Permission isolation boundary for marketplace agents."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str
    isolation_level: IsolationLevel = "basic"
    allowed_resources: tuple[str, ...] = ()
    denied_resources: tuple[str, ...] = ()
    max_concurrent_requests: int = 10


def check_resource_access(boundary: PermissionBoundary, resource: str) -> bool:
    """Check if a resource is accessible within a permission boundary."""
    if resource in boundary.denied_resources:
        return False
    if boundary.allowed_resources and resource not in boundary.allowed_resources:
        return False
    return True


# ---------------------------------------------------------------------------
# PR-076 — Marketplace API contracts
# ---------------------------------------------------------------------------

SortField = Literal["name", "created_at", "rating", "install_count"]


class MarketplaceSearchRequest(BaseModel):
    """Search/filter request for marketplace listings."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    query: str = ""
    category: AgentCategory | None = None
    tags: tuple[str, ...] = ()
    sort_by: SortField = "name"
    page: int = 1
    page_size: int = 20


class MarketplaceListing(BaseModel):
    """A marketplace listing entry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str
    name: str
    description: str = ""
    author: str = ""
    category: AgentCategory = "general"
    latest_version: str = ""
    install_count: int = 0
    average_rating: float = 0.0
    tags: tuple[str, ...] = ()


class MarketplaceSearchResult(BaseModel):
    """Paginated marketplace search result."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    listings: tuple[MarketplaceListing, ...] = ()
    total: int = 0
    page: int = 1
    page_size: int = 20


# ---------------------------------------------------------------------------
# PR-077 — Agent rating
# ---------------------------------------------------------------------------


class AgentRating(BaseModel):
    """User rating for an agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str
    user_id: str
    score: int  # 1-5
    comment: str = ""
    timestamp: float = Field(default_factory=time.time)


class AgentRatingSummary(BaseModel):
    """Aggregated rating summary."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str
    average_score: float = 0.0
    total_ratings: int = 0
    score_distribution: dict[str, int] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# PR-078 — Agent install/update
# ---------------------------------------------------------------------------

InstallStatus = Literal["pending", "installed", "failed", "uninstalled"]


class AgentInstallation(BaseModel):
    """Record of an agent installation in a project."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str
    project_id: str
    version: str
    status: InstallStatus = "pending"
    installed_at: float = Field(default_factory=time.time)
    config: dict[str, Any] = Field(default_factory=dict)


class AgentUpdateRequest(BaseModel):
    """Request to update an installed agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str
    project_id: str
    target_version: str
    auto_migrate_config: bool = True


# ---------------------------------------------------------------------------
# PR-079 — Agent usage analytics
# ---------------------------------------------------------------------------


class AgentUsageMetrics(BaseModel):
    """Usage metrics for a marketplace agent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str
    total_invocations: int = 0
    unique_users: int = 0
    avg_response_time_ms: float = 0.0
    error_rate: float = 0.0
    period_start: float = 0.0
    period_end: float = 0.0


# ---------------------------------------------------------------------------
# In-memory marketplace stub
# ---------------------------------------------------------------------------


class InMemoryMarketplace:
    """Stub marketplace store for testing."""

    def __init__(self) -> None:
        self._manifests: dict[str, AgentManifest] = {}
        self._ratings: list[AgentRating] = []
        self._installations: list[AgentInstallation] = []

    def publish(self, manifest: AgentManifest) -> None:
        self._manifests[manifest.agent_id] = manifest

    def get(self, agent_id: str) -> AgentManifest | None:
        return self._manifests.get(agent_id)

    def search(self, query: str = "") -> list[AgentManifest]:
        if not query:
            return list(self._manifests.values())
        q = query.lower()
        return [
            m
            for m in self._manifests.values()
            if q in m.name.lower() or q in m.description.lower()
        ]

    def rate(self, rating: AgentRating) -> None:
        self._ratings.append(rating)

    def ratings_for(self, agent_id: str) -> list[AgentRating]:
        return [r for r in self._ratings if r.agent_id == agent_id]

    def install(self, installation: AgentInstallation) -> None:
        self._installations.append(installation)

    def installations_for(self, project_id: str) -> list[AgentInstallation]:
        return [i for i in self._installations if i.project_id == project_id]

    def clear(self) -> None:
        self._manifests.clear()
        self._ratings.clear()
        self._installations.clear()
