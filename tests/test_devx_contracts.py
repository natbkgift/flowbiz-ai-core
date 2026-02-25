"""Tests for developer experience contracts (PR-102+)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.contracts.devx import (
    LocalDevCheck,
    LocalDevKitPlan,
    LocalDevServiceSpec,
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
