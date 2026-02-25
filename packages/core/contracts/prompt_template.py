"""Prompt template system contracts."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class PromptTemplateSpec(BaseModel):
    """Prompt template specification."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    template: str
    variables: list[str] = Field(default_factory=list)
    description: str | None = None


class PromptRenderRequest(BaseModel):
    """Input request for template rendering."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    template_name: str
    variables: dict[str, Any] = Field(default_factory=dict)


class PromptRenderResult(BaseModel):
    """Output envelope for template rendering."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: Literal["ok", "error"]
    template_name: str
    prompt: str | None = None
    error: str | None = None
