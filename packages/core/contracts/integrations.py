"""Platform integration contracts/stubs (ecosystem phase).

This module contains contracts and stubs only. Real platform/client integrations
must be implemented outside `flowbiz-ai-core`.

Current contents:
- PR-111: Slack connector
- PR-112: LINE OA connector
- PR-113: WhatsApp connector
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


# ── PR-111: Slack connector (contracts/stubs only) ───────────────────────

SlackEventType = Literal["url_verification", "event_callback", "app_rate_limited"]


class SlackConnectorConfig(BaseModel):
    """Slack connector configuration contract (no secrets or runtime adapter)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    workspace_id: str
    app_id: str
    signing_secret_ref: str = ""
    bot_token_ref: str = ""
    enabled: bool = True
    allowed_event_types: list[str] = Field(default_factory=list)


class SlackEventEnvelope(BaseModel):
    """Incoming Slack webhook/event envelope contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: SlackEventType
    team_id: str = ""
    event_id: str = ""
    event_ts: str = ""
    challenge: str | None = None
    event: dict[str, Any] = Field(default_factory=dict)


class SlackMessageRequest(BaseModel):
    """Outbound Slack message request contract (stub only)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    channel: str
    text: str
    thread_ts: str | None = None
    blocks: list[dict[str, Any]] = Field(default_factory=list)


class SlackConnectorStub:
    """In-memory stub for validating contract flow without Slack integration."""

    def __init__(self) -> None:
        self._sent: list[SlackMessageRequest] = []

    def send(self, request: SlackMessageRequest) -> None:
        self._sent.append(request)

    def sent_messages(self) -> list[SlackMessageRequest]:
        return list(self._sent)


# ── PR-112: LINE OA connector (contracts/stubs only) ─────────────────────

LineEventType = Literal["message", "follow", "unfollow", "postback"]


class LineOAConnectorConfig(BaseModel):
    """LINE OA connector configuration contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    channel_id: str
    channel_secret_ref: str = ""
    channel_access_token_ref: str = ""
    enabled: bool = True


class LineOAWebhookEvent(BaseModel):
    """LINE OA webhook event contract (normalized stub shape)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    event_id: str
    type: LineEventType
    user_id: str = ""
    reply_token: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class LineOAReplyRequest(BaseModel):
    """LINE OA reply/push request contract (stub only)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    to_user_id: str
    messages: list[dict[str, Any]] = Field(default_factory=list)
    reply_token: str | None = None


class LineOAConnectorStub:
    """In-memory LINE OA connector stub for contract testing."""

    def __init__(self) -> None:
        self._replies: list[LineOAReplyRequest] = []

    def send(self, request: LineOAReplyRequest) -> None:
        self._replies.append(request)

    def sent_replies(self) -> list[LineOAReplyRequest]:
        return list(self._replies)


# ── PR-113: WhatsApp connector (contracts/stubs only) ────────────────────

WhatsAppEventType = Literal["message", "status", "template_status"]


class WhatsAppConnectorConfig(BaseModel):
    """WhatsApp connector configuration contract (provider-agnostic stub)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    phone_number_id: str
    business_account_id: str = ""
    access_token_ref: str = ""
    verify_token_ref: str = ""
    enabled: bool = True


class WhatsAppWebhookEvent(BaseModel):
    """Normalized WhatsApp webhook event contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    event_id: str
    type: WhatsAppEventType
    from_user: str = ""
    to_number_id: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


class WhatsAppSendMessageRequest(BaseModel):
    """Outbound WhatsApp message request contract (stub only)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    to_user: str
    message_type: Literal["text", "template"] = "text"
    text: str = ""
    template_name: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WhatsAppConnectorStub:
    """In-memory WhatsApp connector stub for contract testing."""

    def __init__(self) -> None:
        self._messages: list[WhatsAppSendMessageRequest] = []

    def send(self, request: WhatsAppSendMessageRequest) -> None:
        self._messages.append(request)

    def sent_messages(self) -> list[WhatsAppSendMessageRequest]:
        return list(self._messages)
