"""Tests for webhook contracts — PR-046, PR-047."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.contracts.webhook import (
    InMemoryWebhookRegistry,
    WebhookDeliveryResult,
    WebhookPayload,
    WebhookRegistration,
    WebhookRetryPolicy,
    compute_webhook_signature,
    verify_webhook_signature,
)


# ── PR-046: Webhook framework ───────────────────────────────


class TestWebhookRegistration:
    def test_frozen(self) -> None:
        h = WebhookRegistration(webhook_id="h1", url="https://example.com/hook")
        with pytest.raises(ValidationError):
            h.url = "changed"  # type: ignore[misc]

    def test_defaults(self) -> None:
        h = WebhookRegistration(webhook_id="h1", url="https://example.com/hook")
        assert h.active is True
        assert h.events == []
        assert h.secret is None


class TestWebhookPayload:
    def test_payload(self) -> None:
        p = WebhookPayload(
            event="agent.run.completed",
            webhook_id="h1",
            timestamp="2026-01-01T00:00:00Z",
            delivery_id="d1",
            data={"result": "ok"},
        )
        assert p.event == "agent.run.completed"


class TestWebhookDeliveryResult:
    def test_success(self) -> None:
        r = WebhookDeliveryResult(
            delivery_id="d1", webhook_id="h1", status="success", http_status=200
        )
        assert r.status == "success"

    def test_failed(self) -> None:
        r = WebhookDeliveryResult(
            delivery_id="d2",
            webhook_id="h1",
            status="failed",
            http_status=500,
            error="timeout",
        )
        assert r.error == "timeout"


class TestInMemoryWebhookRegistry:
    def test_register_and_get(self) -> None:
        reg = InMemoryWebhookRegistry()
        hook = WebhookRegistration(
            webhook_id="h1",
            url="https://example.com",
            events=["agent.run.completed"],
        )
        reg.register(hook)
        assert reg.get("h1") is not None

    def test_list_for_event(self) -> None:
        reg = InMemoryWebhookRegistry()
        reg.register(
            WebhookRegistration(
                webhook_id="h1",
                url="https://a.com",
                events=["agent.run.completed"],
            )
        )
        reg.register(
            WebhookRegistration(
                webhook_id="h2",
                url="https://b.com",
                events=["workflow.started"],
            )
        )
        matches = reg.list_for_event("agent.run.completed")
        assert len(matches) == 1
        assert matches[0].webhook_id == "h1"

    def test_wildcard_event(self) -> None:
        reg = InMemoryWebhookRegistry()
        reg.register(
            WebhookRegistration(webhook_id="h1", url="https://a.com", events=["*"])
        )
        assert len(reg.list_for_event("anything")) == 1

    def test_inactive_excluded(self) -> None:
        reg = InMemoryWebhookRegistry()
        reg.register(
            WebhookRegistration(
                webhook_id="h1",
                url="https://a.com",
                events=["evt"],
                active=False,
            )
        )
        assert len(reg.list_for_event("evt")) == 0

    def test_remove(self) -> None:
        reg = InMemoryWebhookRegistry()
        reg.register(WebhookRegistration(webhook_id="h1", url="https://a.com"))
        assert reg.remove("h1") is True
        assert reg.remove("h1") is False


# ── PR-047: Webhook retry & signature ────────────────────────


class TestWebhookRetryPolicy:
    def test_defaults(self) -> None:
        p = WebhookRetryPolicy()
        assert p.max_retries == 3
        assert p.backoff_multiplier == 2.0


class TestWebhookSignature:
    def test_compute_and_verify(self) -> None:
        payload = '{"event": "test"}'
        secret = "my-secret"
        sig = compute_webhook_signature(payload, secret)
        assert sig.startswith("sha256=")
        assert verify_webhook_signature(payload, secret, sig) is True

    def test_invalid_signature(self) -> None:
        payload = '{"event": "test"}'
        assert verify_webhook_signature(payload, "secret", "sha256=bad") is False

    def test_different_secrets(self) -> None:
        payload = '{"event": "test"}'
        sig = compute_webhook_signature(payload, "secret-a")
        assert verify_webhook_signature(payload, "secret-b", sig) is False
