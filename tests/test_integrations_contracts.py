"""Tests for platform integration contracts/stubs (PR-111+)."""

from __future__ import annotations

from packages.core.contracts.integrations import (
    EmailAgentConfig,
    EmailAgentStub,
    EmailSendRequest,
    LineOAConnectorConfig,
    LineOAConnectorStub,
    LineOAReplyRequest,
    LineOAWebhookEvent,
    SlackConnectorConfig,
    SlackConnectorStub,
    SlackEventEnvelope,
    SlackMessageRequest,
    WhatsAppConnectorConfig,
    WhatsAppConnectorStub,
    WhatsAppSendMessageRequest,
    WhatsAppWebhookEvent,
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


class TestLineOAConnectorContracts:
    def test_line_config_defaults(self) -> None:
        cfg = LineOAConnectorConfig(channel_id="2001")
        assert cfg.enabled is True

    def test_line_webhook_event(self) -> None:
        event = LineOAWebhookEvent(
            event_id="line-evt-1",
            type="message",
            user_id="U-line",
            payload={"text": "hi"},
        )
        assert event.type == "message"
        assert event.payload["text"] == "hi"

    def test_line_stub_send(self) -> None:
        stub = LineOAConnectorStub()
        stub.send(LineOAReplyRequest(to_user_id="U1", messages=[{"type": "text"}]))
        assert len(stub.sent_replies()) == 1


class TestWhatsAppConnectorContracts:
    def test_whatsapp_config_defaults(self) -> None:
        cfg = WhatsAppConnectorConfig(phone_number_id="P1")
        assert cfg.enabled is True

    def test_whatsapp_webhook_event(self) -> None:
        event = WhatsAppWebhookEvent(
            event_id="wa-evt-1",
            type="message",
            from_user="15551234567",
            payload={"text": {"body": "hello"}},
        )
        assert event.type == "message"
        assert event.payload["text"]["body"] == "hello"

    def test_whatsapp_stub_send(self) -> None:
        stub = WhatsAppConnectorStub()
        stub.send(WhatsAppSendMessageRequest(to_user="1555", text="hello"))
        assert len(stub.sent_messages()) == 1


class TestEmailAgentContracts:
    def test_email_config_defaults(self) -> None:
        cfg = EmailAgentConfig(from_address="noreply@example.com")
        assert cfg.provider == "stub"
        assert cfg.enabled is True

    def test_email_stub_send(self) -> None:
        stub = EmailAgentStub()
        result = stub.send(
            EmailSendRequest(
                to=["user@example.com"],
                subject="Hello",
                body_text="World",
            )
        )
        assert result.accepted is True
        assert result.provider == "stub"
        assert result.message_id == "stub-1"
        assert len(stub.sent_requests()) == 1
