import json

import pytest
from pydantic import ValidationError

from packages.core.contracts.health import HealthResponse
from packages.core.contracts.jobs import JobEnvelope
from packages.core.contracts.meta import RuntimeMeta


def test_health_schema_round_trip_and_immutability():
    schema = HealthResponse(status="ok", service="core", version="1.0.0")

    with pytest.raises(ValidationError):
        schema.service = "other"

    dumped = schema.model_dump()
    assert json.loads(json.dumps(dumped)) == dumped

    loaded = HealthResponse.model_validate(dumped)
    assert loaded == schema


def test_meta_schema_round_trip_and_immutability():
    schema = RuntimeMeta(
        service="core",
        environment="test",
        version="1.0.0",
        build_sha="abc123",
    )

    with pytest.raises(ValidationError):
        schema.version = "2.0.0"

    dumped = schema.model_dump()
    assert json.loads(json.dumps(dumped)) == dumped

    loaded = RuntimeMeta.model_validate(dumped)
    assert loaded == schema


def test_job_envelope_round_trip_and_immutability():
    schema = JobEnvelope(
        job_id="job-1",
        job_type="ingest",
        payload={"count": 2, "items": ["a", "b"]},
        trace_id="trace-1",
        created_at="2024-01-01T00:00:00Z",
    )

    with pytest.raises(ValidationError):
        schema.job_type = "transform"

    dumped = schema.model_dump()
    assert json.loads(json.dumps(dumped)) == dumped

    loaded = JobEnvelope.model_validate(dumped)
    assert loaded == schema
