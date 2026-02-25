"""Tests for PR-028.1 LLM adapter abstraction."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.contracts.llm_adapter import LLMRequest
from packages.core.llm_adapter import StubLLMAdapter


def test_llm_request_validation_and_immutability() -> None:
    request = LLMRequest(trace_id="trace-1", prompt="hello", model="stub-v1")
    assert request.temperature == 0.0
    assert request.max_tokens == 256

    with pytest.raises((ValidationError, AttributeError)):
        request.prompt = "changed"  # type: ignore[misc]


def test_llm_request_rejects_invalid_temperature() -> None:
    with pytest.raises(ValidationError):
        LLMRequest(trace_id="trace-2", prompt="hi", temperature=3.0)


def test_stub_adapter_returns_deterministic_completion() -> None:
    adapter = StubLLMAdapter()
    request = LLMRequest(trace_id="trace-3", prompt="test prompt", model="stub-v1")

    response = adapter.complete(request)

    assert response.status == "ok"
    assert response.trace_id == "trace-3"
    assert response.model == "stub-v1"
    assert response.content == "STUB[stub-v1]: test prompt"
    assert response.finish_reason == "stop"


def test_stub_adapter_info() -> None:
    info = StubLLMAdapter().info
    assert info.adapter_name == "stub"
    assert info.provider == "local"
    assert info.supports_streaming is False
