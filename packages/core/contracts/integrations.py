"""Platform integration contracts/stubs (ecosystem phase).

This module contains contracts and stubs only. Real platform/client integrations
must be implemented outside `flowbiz-ai-core`.

Current contents:
- PR-111: Slack connector
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
