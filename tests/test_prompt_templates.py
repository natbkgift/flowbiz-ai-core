"""Tests for PR-028.2 prompt template system."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.contracts.prompt_template import PromptRenderRequest, PromptTemplateSpec
from packages.core.prompt_templates import PromptTemplateRegistry


def test_prompt_template_contract_immutability() -> None:
    spec = PromptTemplateSpec(
        name="greeting",
        template="Hello {name}",
        variables=["name"],
    )

    with pytest.raises((ValidationError, AttributeError)):
        spec.name = "changed"  # type: ignore[misc]


def test_register_and_list_template_names_sorted() -> None:
    registry = PromptTemplateRegistry()
    registry.register(PromptTemplateSpec(name="z", template="Z", variables=[]))
    registry.register(PromptTemplateSpec(name="a", template="A", variables=[]))

    assert registry.list_names() == ["a", "z"]


def test_render_success() -> None:
    registry = PromptTemplateRegistry()
    registry.register(
        PromptTemplateSpec(
            name="summary",
            template="Summarize: {text}",
            variables=["text"],
        )
    )

    result = registry.render(
        PromptRenderRequest(template_name="summary", variables={"text": "hello"})
    )

    assert result.status == "ok"
    assert result.prompt == "Summarize: hello"


def test_render_missing_and_undeclared_variables() -> None:
    registry = PromptTemplateRegistry()
    registry.register(
        PromptTemplateSpec(
            name="qa",
            template="Q: {question} A: {answer}",
            variables=["question", "answer"],
        )
    )

    missing = registry.render(
        PromptRenderRequest(template_name="qa", variables={"question": "Why?"})
    )
    assert missing.status == "error"
    assert "Missing template variables" in (missing.error or "")

    undeclared = registry.render(
        PromptRenderRequest(
            template_name="qa",
            variables={"question": "Why?", "answer": "Because", "extra": "x"},
        )
    )
    assert undeclared.status == "error"
    assert "Undeclared template variables" in (undeclared.error or "")


def test_render_fails_for_unknown_template() -> None:
    registry = PromptTemplateRegistry()
    result = registry.render(PromptRenderRequest(template_name="missing", variables={}))

    assert result.status == "error"
    assert "not found" in (result.error or "")
