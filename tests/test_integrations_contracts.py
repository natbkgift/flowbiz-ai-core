"""Tests for platform integration contracts/stubs (PR-111+)."""

from __future__ import annotations

from packages.core.contracts.integrations import (
    SlackConnectorConfig,
    SlackConnectorStub,
    SlackEventEnvelope,
    SlackMessageRequest,
)


class TestSlackConnectorContracts:
    def test_slack_config_defaults(self) -> None:
        cfg = SlackConnectorConfig(workspace_id="T1", app_id="A1")
        assert cfg.enabled is True
        assert cfg.allowed_event_types == []

    def test_slack_event_envelope(self) -> None:
        env = SlackEventEnvelope(
            type="event_callback",
            team_id="T1",
            event_id="Ev1",
            event={"type": "app_mention"},
        )
        assert env.type == "event_callback"
        assert env.event["type"] == "app_mention"

    def test_slack_stub_send(self) -> None:
        stub = SlackConnectorStub()
        req = SlackMessageRequest(channel="C1", text="hello")
        stub.send(req)
        sent = stub.sent_messages()
        assert len(sent) == 1
        assert sent[0].text == "hello"
