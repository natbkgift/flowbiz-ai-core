"""Tests for Pydantic schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from packages.core.schemas import ErrorPayload, ErrorResponse, HealthResponse, MetaResponse


@pytest.mark.parametrize(
    "response_cls, data",
    [
        pytest.param(HealthResponse, {"status": "ok", "service": "flowbiz", "version": "1.0.0"}, id="health-response"),
        pytest.param(MetaResponse, {"service": "flowbiz", "env": "test", "version": "1.0.0"}, id="meta-response"),
    ],
)
def test_response_dump_matches_payload(response_cls, data):
    response = response_cls(**data)

    assert response.model_dump() == data


def test_error_response_excludes_none_details():
    payload = ErrorPayload(code="HTTP_500", message="boom", request_id="abc-123")
    response = ErrorResponse(error=payload)

    assert response.model_dump() == {
        "error": {
            "code": "HTTP_500",
            "message": "boom",
            "request_id": "abc-123",
        }
    }


def test_error_response_includes_details_when_provided():
    payload = ErrorPayload(
        code="HTTP_400", message="bad", request_id="abc-123", details=["detail"]
    )
    response = ErrorResponse(error=payload)

    assert response.model_dump() == {
        "error": {
            "code": "HTTP_400",
            "message": "bad",
            "request_id": "abc-123",
            "details": ["detail"],
        }
    }


def test_schema_forbids_extra_fields():
    with pytest.raises(ValidationError):
        HealthResponse(status="ok", service="flowbiz", version="1.0.0", extra="x")
