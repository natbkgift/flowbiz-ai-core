"""Tests for example agents (PR-104)."""

from __future__ import annotations

from packages.core.agents.context import AgentContext
from packages.core.agents.examples import MetadataEchoAgent, TemplateReplyAgent


class TestTemplateReplyAgent:
    def test_deterministic_reply(self) -> None:
        agent = TemplateReplyAgent()
        ctx = AgentContext.create(
            input_text="hello world",
            request_id="req-1",
            channel="api",
        )
        result = agent.run(ctx)
        assert result.status == "ok"
        assert result.output_text == "[template-reply] hello world"
        assert result.trace["agent_name"] == "example.template_reply"
        assert result.trace["request_id"] == "req-1"


class TestMetadataEchoAgent:
    def test_sorted_metadata_keys(self) -> None:
        agent = MetadataEchoAgent()
        ctx = AgentContext.create(
            input_text="inspect",
            request_id="req-2",
            metadata={"z": 1, "a": 2, "m": 3},
        )
        result = agent.run(ctx)
        assert result.status == "ok"
        assert result.output_text == "metadata_keys=a,m,z"
        assert result.trace["metadata_key_count"] == 3

    def test_empty_metadata(self) -> None:
        agent = MetadataEchoAgent()
        ctx = AgentContext.create(input_text="inspect")
        result = agent.run(ctx)
        assert result.output_text == "metadata_keys=<none>"
