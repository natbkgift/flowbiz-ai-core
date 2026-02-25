"""Webhook contracts — PR-046, PR-047.

PR-046: Webhook framework — registration, delivery, payload contracts.
PR-047: Webhook retry & signature verification contracts.

These are schema-only contracts with in-memory stubs; actual HTTP
delivery and signature verification belong in the platform layer.
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# ── PR-046: Webhook framework ───────────────────────────────

WebhookEvent = Literal[
    "agent.run.started",
    "agent.run.completed",
    "agent.run.failed",
    "workflow.started",
    "workflow.completed",
    "workflow.failed",
    "workflow.paused",
    "tool.executed",
]


class WebhookRegistration(BaseModel):
    """A registered webhook endpoint."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    webhook_id: str = Field(..., description="Unique webhook identifier")
    url: str = Field(..., description="Delivery URL")
    events: list[str] = Field(
        default_factory=list, description="Subscribed event types"
    )
    active: bool = Field(True, description="Whether deliveries are enabled")
    secret: str | None = Field(None, description="Shared secret for HMAC signing")
    metadata: dict[str, Any] = Field(default_factory=dict)


class WebhookPayload(BaseModel):
    """Standard webhook delivery payload."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    event: str = Field(..., description="Event type")
    webhook_id: str = Field(..., description="Target webhook")
    timestamp: str = Field(..., description="ISO 8601 event time")
    data: dict[str, Any] = Field(default_factory=dict)
    delivery_id: str = Field(..., description="Unique delivery attempt ID")


class WebhookDeliveryResult(BaseModel):
    """Result of a webhook delivery attempt."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    delivery_id: str
    webhook_id: str
    status: Literal["success", "failed", "pending"]
    http_status: int | None = Field(None, description="Response status code")
    attempt: int = Field(1, description="Attempt number")
    error: str | None = None


class InMemoryWebhookRegistry:
    """In-memory webhook registration store (stub)."""

    def __init__(self) -> None:
        self._hooks: dict[str, WebhookRegistration] = {}

    def register(self, hook: WebhookRegistration) -> None:
        self._hooks[hook.webhook_id] = hook

    def get(self, webhook_id: str) -> WebhookRegistration | None:
        return self._hooks.get(webhook_id)

    def list_for_event(self, event: str) -> list[WebhookRegistration]:
        return [
            h
            for h in self._hooks.values()
            if h.active and (event in h.events or "*" in h.events)
        ]

    def remove(self, webhook_id: str) -> bool:
        return self._hooks.pop(webhook_id, None) is not None


# ── PR-047: Webhook retry & signature ────────────────────────


class WebhookRetryPolicy(BaseModel):
    """Retry policy for webhook deliveries."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    max_retries: int = Field(3, description="Maximum delivery attempts")
    backoff_seconds: float = Field(5.0, description="Initial backoff between retries")
    backoff_multiplier: float = Field(2.0, description="Exponential backoff factor")


def compute_webhook_signature(
    payload_json: str, secret: str, algorithm: str = "sha256"
) -> str:
    """Compute HMAC signature for a webhook payload.

    Returns a hex digest string prefixed with the algorithm name,
    e.g. ``sha256=abc123...``.
    """
    mac = hmac.new(secret.encode(), payload_json.encode(), getattr(hashlib, algorithm))
    return f"{algorithm}={mac.hexdigest()}"


def verify_webhook_signature(
    payload_json: str,
    secret: str,
    signature: str,
    algorithm: str = "sha256",
) -> bool:
    """Verify a webhook signature against the expected HMAC."""
    expected = compute_webhook_signature(payload_json, secret, algorithm)
    return hmac.compare_digest(expected, signature)
