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
        self._templates: dict[str, dict[str, PromptTemplateSpec]] = {}
        self._latest_version: dict[str, str] = {}

    def register(self, spec: PromptTemplateSpec) -> PromptTemplateSpec:
        """Register or overwrite a prompt template spec by name."""
        versioned = self._templates.setdefault(spec.name, {})
        versioned[spec.version] = spec
        self._latest_version[spec.name] = spec.version
        return spec

    def get(self, name: str, version: str | None = None) -> PromptTemplateSpec | None:
        """Get template spec by name."""
        versioned = self._templates.get(name)
        if versioned is None:
            return None

        resolved_version = version or self._latest_version.get(name)
        if resolved_version is None:
            return None

        return versioned.get(resolved_version)

    def list_names(self) -> list[str]:
        """List registered template names in deterministic sorted order."""
        return sorted(self._templates.keys())

    def list_versions(self, name: str) -> list[str]:
        """List known versions for a template in deterministic sorted order."""
        versioned = self._templates.get(name, {})
        return sorted(versioned.keys())

    def render(self, request: PromptRenderRequest) -> PromptRenderResult:
        """Render a prompt from a template with strict variable validation."""
        spec = self.get(request.template_name, version=request.version)
        if spec is None:
            return PromptRenderResult(
                status="error",
                template_name=request.template_name,
                version=request.version,
                error=f"Template '{request.template_name}' not found",
            )

        expected_vars = set(spec.variables)
        received_vars = set(request.variables.keys())

        missing = sorted(expected_vars - received_vars)
        if missing:
            return PromptRenderResult(
                status="error",
                template_name=request.template_name,
                version=spec.version,
                error=f"Missing template variables: {', '.join(missing)}",
            )

        undeclared = sorted(received_vars - expected_vars)
        if undeclared:
            return PromptRenderResult(
                status="error",
                template_name=request.template_name,
                version=spec.version,
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
                version=spec.version,
                error=(
                    "Declared variables not referenced in template: "
                    f"{', '.join(unreferenced)}"
                ),
            )

        rendered = spec.template.format(**request.variables)
        return PromptRenderResult(
            status="ok",
            template_name=request.template_name,
            version=spec.version,
            prompt=rendered,
        )
