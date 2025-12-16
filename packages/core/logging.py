"""Structured logging utilities for FlowBiz AI Core."""

from __future__ import annotations

import logging
import sys
from typing import Final

from .config import get_settings

LOG_FORMAT: Final[str] = "%(asctime)s | %(levelname)s | %(message)s | request_id=%(request_id)s"


class RequestIdFormatter(logging.Formatter):
    """Formatter that ensures a request ID field is present."""

    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - trivial
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return super().format(record)


def get_logger(name: str) -> logging.Logger:
    """Return a structured logger configured from application settings."""

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(RequestIdFormatter(LOG_FORMAT))

    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False

    return logger
