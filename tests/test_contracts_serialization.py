import json
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from packages.core.contracts.health import HealthResponse
from packages.core.contracts.jobs import JobEnvelope
from packages.core.contracts.meta import RuntimeMeta


@pytest.mark.parametrize(
    "schema_class, instance_data, update_field, update_value",
    [
        (
            HealthResponse,
            {"status": "ok", "service": "core", "version": "1.0.0"},
            "service",
            "other",
        ),
        (
            RuntimeMeta,
            {
                "service": "core",
                "environment": "test",
                "version": "1.0.0",
                "build_sha": "abc123",
            },
            "version",
            "2.0.0",
        ),
        (
            JobEnvelope,
            {
                "job_id": "job-1",
                "job_type": "ingest",
                "payload": {"count": 2, "items": ["a", "b"]},
                "trace_id": "trace-1",
                "created_at": "2024-01-01T00:00:00Z",
            },
            "job_type",
            "transform",
        ),
    ],
)
def test_schema_round_trip_and_immutability(
    schema_class: type[BaseModel],
    instance_data: dict[str, Any],
    update_field: str,
    update_value: Any,
):
    """Tests schema immutability and serialization round-trip."""
    schema = schema_class(**instance_data)

    with pytest.raises((ValidationError, AttributeError)):
        setattr(schema, update_field, update_value)

    dumped = schema.model_dump()
    loaded = schema_class.model_validate(dumped)
    assert loaded == schema
    assert json.loads(json.dumps(dumped)) == dumped

    json_dumped = schema.model_dump_json()
    json_loaded = schema_class.model_validate_json(json_dumped)
    assert json_loaded == schema


def test_optional_fields_can_be_omitted():
    """Test that optional fields can be omitted from schema instantiation."""
    # RuntimeMeta with build_sha omitted
    meta = RuntimeMeta(
        service="core",
        environment="test",
        version="1.0.0",
    )
    assert meta.build_sha is None
    assert meta.service == "core"

    # JobEnvelope with trace_id and created_at omitted
    job = JobEnvelope(
        job_id="job-1",
        job_type="ingest",
        payload={"data": "value"},
    )
    assert job.trace_id is None
    assert job.created_at is None
    assert job.job_id == "job-1"


def test_invalid_inputs_raise_validation_errors():
    """Test that invalid inputs raise validation errors."""
    # HealthResponse with invalid status value
    with pytest.raises(ValidationError):
        HealthResponse(status="invalid_status", service="core", version="1.0.0")

    # HealthResponse with missing required field
    with pytest.raises(ValidationError):
        HealthResponse(status="ok", version="1.0.0")

    # RuntimeMeta with wrong type for version
    with pytest.raises(ValidationError):
        RuntimeMeta(service="core", environment="test", version=123)

    # JobEnvelope with non-dict payload
    with pytest.raises(ValidationError):
        JobEnvelope(job_id="job-1", job_type="ingest", payload="not a dict")

    # JobEnvelope with missing required field
    with pytest.raises(ValidationError):
        JobEnvelope(job_id="job-1", payload={"data": "value"})


def test_extra_fields_are_forbidden():
    """Test that schemas reject extra fields not defined in the model."""
    # HealthResponse with extra field
    with pytest.raises(ValidationError):
        HealthResponse(
            status="ok",
            service="core",
            version="1.0.0",
            extra_field="should fail",
        )

    # RuntimeMeta with extra field
    with pytest.raises(ValidationError):
        RuntimeMeta(
            service="core",
            environment="test",
            version="1.0.0",
            unknown_field="should fail",
        )

    # JobEnvelope with extra field
    with pytest.raises(ValidationError):
        JobEnvelope(
            job_id="job-1",
            job_type="ingest",
            payload={"data": "value"},
            unexpected="should fail",
        )
