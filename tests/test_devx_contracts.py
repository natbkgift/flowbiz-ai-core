"""Tests for developer experience contracts (PR-102+)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.contracts.devx import (
    LocalDevCheck,
    LocalDevKitPlan,
    LocalDevServiceSpec,
    SeedTemplateFile,
    SeedTemplateManifest,
    SeedTemplateVariable,
    required_template_variables,
    summarize_local_dev_kit,
)


class TestLocalDevServiceSpec:
    def test_minimal_service(self) -> None:
        spec = LocalDevServiceSpec(service_name="api", service_type="api")
        assert spec.required is True
        assert spec.ports == []
        assert spec.env_keys == []

    def test_forbid_extra(self) -> None:
        with pytest.raises(ValidationError):
            LocalDevServiceSpec(  # type: ignore[call-arg]
                service_name="api",
                service_type="api",
                unknown=True,
            )


class TestLocalDevKitPlan:
    def test_defaults(self) -> None:
        plan = LocalDevKitPlan(kit_id="dev-default")
        assert plan.profile == "default"
        assert plan.services == []
        assert plan.checks == []

    def test_summary_counts(self) -> None:
        plan = LocalDevKitPlan(
            kit_id="dev-default",
            services=[
                LocalDevServiceSpec(service_name="api", service_type="api"),
                LocalDevServiceSpec(
                    service_name="jaeger-mock",
                    service_type="observability",
                    required=False,
                ),
            ],
            checks=[
                LocalDevCheck(check_name="python-version", status="pass"),
                LocalDevCheck(check_name="env-file", status="warn"),
                LocalDevCheck(check_name="db-port", status="fail"),
            ],
        )
        summary = summarize_local_dev_kit(plan)
        assert summary["service_count"] == 2
        assert summary["required_service_count"] == 1
        assert summary["check_count"] == 3
        assert summary["check_warn_count"] == 1
        assert summary["check_fail_count"] == 1


class TestSeedTemplateManifest:
    def test_manifest_defaults(self) -> None:
        manifest = SeedTemplateManifest(template_id="agent-basic", name="Agent Basic")
        assert manifest.version == "1.0.0"
        assert manifest.category == "agent"
        assert manifest.variables == []
        assert manifest.files == []

    def test_required_template_variables(self) -> None:
        manifest = SeedTemplateManifest(
            template_id="workflow-basic",
            name="Workflow Basic",
            category="workflow",
            variables=[
                SeedTemplateVariable(key="project_name", required=True),
                SeedTemplateVariable(key="author", required=False),
                SeedTemplateVariable(key="persona", required=True, default="core"),
            ],
            files=[
                SeedTemplateFile(path="README.md", mode="template"),
                SeedTemplateFile(path=".gitignore", mode="static"),
            ],
        )
        assert required_template_variables(manifest) == ["project_name", "persona"]

    def test_manifest_forbid_extra(self) -> None:
        with pytest.raises(ValidationError):
            SeedTemplateManifest(  # type: ignore[call-arg]
                template_id="bad",
                name="Bad",
                extra_field=True,
            )
