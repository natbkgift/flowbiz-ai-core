"""LLM adapter abstraction contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LLMRequest(BaseModel):
    """Transport-agnostic LLM request contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    trace_id: str
    prompt: str
    temperature: float = Field(0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(256, ge=1)
    model: str = "stub-model"


class LLMResponse(BaseModel):
    """Transport-agnostic LLM response contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: Literal["ok", "error"]
    trace_id: str
    content: str | None = None
    model: str
    finish_reason: str | None = None
    error_code: str | None = None


class LLMAdapterInfo(BaseModel):
    """Metadata describing an adapter implementation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    adapter_name: str
    provider: str
    supports_streaming: bool = False
