"""LLM adapter abstraction and deterministic stub implementation."""

from __future__ import annotations

from typing import Protocol

from .contracts.llm_adapter import LLMAdapterInfo, LLMRequest, LLMResponse


class LLMAdapterProtocol(Protocol):
    """Protocol for provider-agnostic LLM adapters."""

    @property
    def info(self) -> LLMAdapterInfo:
        """Adapter metadata."""
        ...

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Generate a completion for the request payload."""
        ...


class StubLLMAdapter:
    """Deterministic stub adapter for local/testing usage."""

    @property
    def info(self) -> LLMAdapterInfo:
        return LLMAdapterInfo(
            adapter_name="stub",
            provider="local",
            supports_streaming=False,
        )

    def complete(self, request: LLMRequest) -> LLMResponse:
        content = f"STUB[{request.model}]: {request.prompt}"
        return LLMResponse(
            status="ok",
            trace_id=request.trace_id,
            content=content,
            model=request.model,
            finish_reason="stop",
        )
