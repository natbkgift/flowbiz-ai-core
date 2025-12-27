from datetime import datetime, timezone
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

    with pytest.raises((ValidationError, AttributeError)):
        schema.job_type = "transform"

    dumped = schema.model_dump()
    assert json.loads(json.dumps(dumped)) == dumped

    loaded = JobEnvelope.model_validate(dumped)
    assert loaded == schema
=======
    json_dumped = schema.model_dump_json()
    json_loaded = schema_class.model_validate_json(json_dumped)
    assert json_loaded == schema
>>>>>>> origin/codex/create-schema-only-contract-package
