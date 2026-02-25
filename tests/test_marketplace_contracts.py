"""Tests for marketplace contracts — PR-071 to PR-080."""

from __future__ import annotations

from packages.core.contracts.marketplace import (
    AgentInstallation,
    AgentManifest,
    AgentRating,
    AgentRatingSummary,
    AgentUpdateRequest,
    AgentUsageMetrics,
    AgentVersion,
    InMemoryMarketplace,
    MarketplaceListing,
    MarketplaceSearchRequest,
    MarketplaceSearchResult,
    PermissionBoundary,
    SandboxConfig,
    SandboxState,
    ToolManifest,
    check_resource_access,
)


class TestAgentManifest:
    def test_schema(self) -> None:
        m = AgentManifest(
            agent_id="echo",
            name="Echo Agent",
            version="1.0.0",
            category="general",
            tags=("test",),
            required_tools=("dummy",),
        )
        assert m.agent_id == "echo"
        assert m.min_core_version == "0.1.0"

    def test_frozen(self) -> None:
        m = AgentManifest(agent_id="x", name="X", version="1.0.0")
        try:
            m.name = "Y"  # type: ignore[misc]
            assert False
        except Exception:
            pass


class TestToolManifest:
    def test_schema(self) -> None:
        t = ToolManifest(
            tool_id="search", name="Search Tool", version="1.0.0", category="api"
        )
        assert t.category == "api"


class TestAgentVersion:
    def test_defaults(self) -> None:
        v = AgentVersion(agent_id="echo", version="1.0.0")
        assert v.status == "draft"
        assert v.published_at is None


class TestSandboxConfig:
    def test_defaults(self) -> None:
        s = SandboxConfig(agent_id="echo")
        assert s.memory_limit_mb == 256
        assert s.network_access is False


class TestSandboxState:
    def test_defaults(self) -> None:
        s = SandboxState(agent_id="echo")
        assert s.status == "stopped"
        assert s.invocation_count == 0


class TestPermissionBoundary:
    def test_default_allows_all(self) -> None:
        b = PermissionBoundary(agent_id="echo")
        assert check_resource_access(b, "anything") is True

    def test_denied_resource(self) -> None:
        b = PermissionBoundary(agent_id="echo", denied_resources=("secrets",))
        assert check_resource_access(b, "secrets") is False
        assert check_resource_access(b, "files") is True

    def test_allowlist_only(self) -> None:
        b = PermissionBoundary(agent_id="echo", allowed_resources=("files", "api"))
        assert check_resource_access(b, "files") is True
        assert check_resource_access(b, "secrets") is False


class TestMarketplaceSearchRequest:
    def test_defaults(self) -> None:
        r = MarketplaceSearchRequest()
        assert r.page == 1
        assert r.page_size == 20


class TestMarketplaceListing:
    def test_schema(self) -> None:
        listing = MarketplaceListing(agent_id="echo", name="Echo", install_count=42)
        assert listing.install_count == 42


class TestMarketplaceSearchResult:
    def test_empty(self) -> None:
        r = MarketplaceSearchResult()
        assert r.listings == ()
        assert r.total == 0


class TestAgentRating:
    def test_schema(self) -> None:
        r = AgentRating(agent_id="echo", user_id="u1", score=5, comment="Great!")
        assert r.score == 5


class TestAgentRatingSummary:
    def test_defaults(self) -> None:
        s = AgentRatingSummary(agent_id="echo")
        assert s.average_score == 0.0
        assert s.total_ratings == 0


class TestAgentInstallation:
    def test_defaults(self) -> None:
        i = AgentInstallation(agent_id="echo", project_id="p1", version="1.0.0")
        assert i.status == "pending"


class TestAgentUpdateRequest:
    def test_schema(self) -> None:
        u = AgentUpdateRequest(agent_id="echo", project_id="p1", target_version="2.0.0")
        assert u.auto_migrate_config is True


class TestAgentUsageMetrics:
    def test_defaults(self) -> None:
        m = AgentUsageMetrics(agent_id="echo")
        assert m.total_invocations == 0
        assert m.error_rate == 0.0


class TestInMemoryMarketplace:
    def test_publish_and_get(self) -> None:
        mp = InMemoryMarketplace()
        m = AgentManifest(agent_id="echo", name="Echo", version="1.0.0")
        mp.publish(m)
        assert mp.get("echo") is not None
        assert mp.get("echo").name == "Echo"

    def test_search(self) -> None:
        mp = InMemoryMarketplace()
        mp.publish(AgentManifest(agent_id="a", name="Alpha Bot", version="1.0.0"))
        mp.publish(AgentManifest(agent_id="b", name="Beta Bot", version="1.0.0"))
        results = mp.search("alpha")
        assert len(results) == 1
        assert results[0].agent_id == "a"

    def test_search_all(self) -> None:
        mp = InMemoryMarketplace()
        mp.publish(AgentManifest(agent_id="a", name="A", version="1.0.0"))
        mp.publish(AgentManifest(agent_id="b", name="B", version="1.0.0"))
        assert len(mp.search()) == 2

    def test_rate(self) -> None:
        mp = InMemoryMarketplace()
        mp.rate(AgentRating(agent_id="echo", user_id="u1", score=5))
        mp.rate(AgentRating(agent_id="echo", user_id="u2", score=4))
        assert len(mp.ratings_for("echo")) == 2

    def test_install(self) -> None:
        mp = InMemoryMarketplace()
        mp.install(AgentInstallation(agent_id="echo", project_id="p1", version="1.0.0"))
        assert len(mp.installations_for("p1")) == 1

    def test_clear(self) -> None:
        mp = InMemoryMarketplace()
        mp.publish(AgentManifest(agent_id="a", name="A", version="1.0.0"))
        mp.rate(AgentRating(agent_id="a", user_id="u1", score=5))
        mp.install(AgentInstallation(agent_id="a", project_id="p1", version="1.0.0"))
        mp.clear()
        assert mp.search() == []
        assert mp.ratings_for("a") == []
        assert mp.installations_for("p1") == []
