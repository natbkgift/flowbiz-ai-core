import logging
from apps.api.main import app
from packages.core import get_settings
from packages.core.logging import RequestIdFormatter, get_logger
from tests._requires import requires_httpx


def test_get_logger_configures_structured_handler():
    settings = get_settings()
    expected_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger = get_logger("tests.logging")

    assert logger.level == expected_level
    assert logger.handlers, "Logger should have at least one handler configured"

    handler = logger.handlers[0]
    assert isinstance(handler.formatter, RequestIdFormatter)

    record = logging.LogRecord(
        name="tests.logging", level=logging.INFO, pathname=__file__, lineno=1, msg="hello", args=(), exc_info=None
    )
    formatted = handler.format(record)

    assert "request_id=-" in formatted


@requires_httpx
def test_app_startup_initializes_logger_state():
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        assert hasattr(client.app.state, "logger")
        assert client.app.state.logger.name == "flowbiz.api"
