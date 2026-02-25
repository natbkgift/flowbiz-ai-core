"""Tests for OpenAPI schema hardening — PR-049."""

from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import create_app
from packages.core import get_version_info


def _get_openapi() -> dict:
    client = TestClient(create_app())
    r = client.get("/openapi.json")
    assert r.status_code == 200
    return r.json()


class TestOpenAPIHardening:
    def test_openapi_version(self) -> None:
        schema = _get_openapi()
        assert schema.get("openapi", "").startswith("3.")

    def test_info_title(self) -> None:
        schema = _get_openapi()
        assert schema["info"]["title"]

    def test_info_version_matches_runtime_version(self) -> None:
        schema = _get_openapi()
        assert schema["info"]["version"] == get_version_info().version

    def test_paths_not_empty(self) -> None:
        schema = _get_openapi()
        assert len(schema["paths"]) > 0

    def test_healthz_path_exists(self) -> None:
        schema = _get_openapi()
        assert "/healthz" in schema["paths"]

    def test_agent_run_path_exists(self) -> None:
        schema = _get_openapi()
        assert "/v1/agent/run" in schema["paths"]

    def test_agent_tools_path_exists(self) -> None:
        schema = _get_openapi()
        assert "/v1/agent/tools" in schema["paths"]

    def test_agent_health_path_exists(self) -> None:
        schema = _get_openapi()
        assert "/v1/agent/health" in schema["paths"]

    def test_v2_meta_path_exists(self) -> None:
        schema = _get_openapi()
        assert "/v2/meta" in schema["paths"]

    def test_schemas_section_exists(self) -> None:
        schema = _get_openapi()
        components = schema.get("components", {})
        assert "schemas" in components

    def test_health_response_schema_exists(self) -> None:
        schema = _get_openapi()
        schemas = schema.get("components", {}).get("schemas", {})
        assert "HealthResponse" in schemas
