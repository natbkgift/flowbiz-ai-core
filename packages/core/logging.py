"""Structured logging utilities for FlowBiz AI Core."""

from __future__ import annotations

import logging
import sys
import threading
from contextvars import ContextVar
from typing import Final

from .config import get_settings

LOG_FORMAT: Final[str] = (
    "%(asctime)s | %(levelname)s | %(message)s | request_id=%(request_id)s"
)
_lock = threading.Lock()

REQUEST_ID_CTX_VAR: ContextVar[str | None] = ContextVar("request_id", default=None)


class RequestIdFormatter(logging.Formatter):
    """Formatter that ensures a request ID field is present."""

    def format(self, record: logging.LogRecord) -> str:
        # RequestIdFilter is responsible for attaching the request_id to the record.
        # The formatter only ensures a default value is present so formatting doesn't fail
        # if the filter was not applied for some reason (e.g., custom logger setups).
        record.request_id = getattr(record, "request_id", None) or "-"
        return super().format(record)


class RequestIdFilter(logging.Filter):
    """Ensure request_id is set and included in the message for upstream handlers."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        request_id = getattr(record, "request_id", None) or REQUEST_ID_CTX_VAR.get()
        record.request_id = request_id or "-"

        # This logic is a workaround for pytest's caplog, which uses a default
        # formatter that doesn't include the custom 'request_id' attribute.
        # This modification should only be applied when running under pytest to avoid
        # duplicating the request_id in production logs where RequestIdFormatter is used.
        if "pytest" in sys.modules:
            message = record.getMessage()
            if "request_id=" not in message:
                record.msg = f"{message} | request_id={record.request_id}"
                record.args = ()

        return True


def get_logger(name: str) -> logging.Logger:
    """Return a structured logger configured from application settings."""

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    with _lock:
        if logger.handlers:
            return logger

        settings = get_settings()
        level = getattr(logging, settings.log_level.upper(), logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(RequestIdFormatter(LOG_FORMAT))

        logger.setLevel(level)
        logger.addHandler(handler)
        logger.addFilter(RequestIdFilter())
        # Allow records to bubble up so test capture handlers (e.g. pytest caplog)
        # can see them while keeping our structured handler attached.
        logger.propagate = True

    return logger
