"""Prompt template registry and rendering utilities."""

from __future__ import annotations

from string import Formatter

from .contracts.prompt_template import (
    PromptRenderRequest,
    PromptRenderResult,
    PromptTemplateSpec,
)


class PromptTemplateRegistry:
    """Deterministic in-memory prompt template registry."""

    def __init__(self) -> None:
        self._templates: dict[str, PromptTemplateSpec] = {}

    def register(self, spec: PromptTemplateSpec) -> PromptTemplateSpec:
        """Register or overwrite a prompt template spec by name."""
        self._templates[spec.name] = spec
        return spec

    def get(self, name: str) -> PromptTemplateSpec | None:
        """Get template spec by name."""
        return self._templates.get(name)

    def list_names(self) -> list[str]:
        """List registered template names in deterministic sorted order."""
        return sorted(self._templates.keys())

    def render(self, request: PromptRenderRequest) -> PromptRenderResult:
        """Render a prompt from a template with strict variable validation."""
        spec = self.get(request.template_name)
        if spec is None:
            return PromptRenderResult(
                status="error",
                template_name=request.template_name,
                error=f"Template '{request.template_name}' not found",
            )

        expected_vars = set(spec.variables)
        received_vars = set(request.variables.keys())

        missing = sorted(expected_vars - received_vars)
        if missing:
            return PromptRenderResult(
                status="error",
                template_name=request.template_name,
                error=f"Missing template variables: {', '.join(missing)}",
            )

        undeclared = sorted(received_vars - expected_vars)
        if undeclared:
            return PromptRenderResult(
                status="error",
                template_name=request.template_name,
                error=f"Undeclared template variables: {', '.join(undeclared)}",
            )

        referenced = {
            field_name
            for _, field_name, _, _ in Formatter().parse(spec.template)
            if field_name
        }
        unreferenced = sorted(expected_vars - referenced)
        if unreferenced:
            return PromptRenderResult(
                status="error",
                template_name=request.template_name,
                error=(
                    "Declared variables not referenced in template: "
                    f"{', '.join(unreferenced)}"
                ),
            )

        rendered = spec.template.format(**request.variables)
        return PromptRenderResult(
            status="ok",
            template_name=request.template_name,
            prompt=rendered,
        )
