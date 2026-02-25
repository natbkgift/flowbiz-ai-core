"""Deterministic example agents for developer reference (PR-104)."""

from __future__ import annotations

from .base import AgentBase
from .context import AgentContext
from .result import AgentResult


class TemplateReplyAgent(AgentBase):
    """Formats a deterministic response using a fixed prefix and suffix."""

    def __init__(self, name: str = "example.template_reply") -> None:
        super().__init__(name=name)

    def run(self, ctx: AgentContext) -> AgentResult:
        text = ctx.input_text.strip()
        return AgentResult(
            output_text=f"[template-reply] {text}",
            status="ok",
            reason=None,
            trace={
                "agent_name": self.name,
                "channel": ctx.channel,
                "request_id": ctx.request_id,
            },
        )


class MetadataEchoAgent(AgentBase):
    """Echoes selected context metadata keys in stable sorted order."""

    def __init__(self, name: str = "example.metadata_echo") -> None:
        super().__init__(name=name)

    def run(self, ctx: AgentContext) -> AgentResult:
        keys = sorted(ctx.metadata.keys())
        key_list = ",".join(keys) if keys else "<none>"
        return AgentResult(
            output_text=f"metadata_keys={key_list}",
            status="ok",
            reason=None,
            trace={
                "agent_name": self.name,
                "metadata_key_count": len(keys),
                "request_id": ctx.request_id,
            },
        )
