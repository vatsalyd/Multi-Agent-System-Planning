"""
Centralized logging configuration — structured JSON output + correlation ID support.
"""

import logging
import contextvars
from pythonjsonlogger import json as json_formatter

# Correlation ID propagated through the request lifecycle
correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default=""
)


class CorrelationFilter(logging.Filter):
    """Inject correlation_id into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id.get("")
        return True


def setup_logging(level: str = "INFO") -> None:
    """Configure structured JSON logging with correlation ID support."""
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicate output
    root.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(
        json_formatter.JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(correlation_id)s %(message)s",
            rename_fields={
                "asctime": "timestamp",
                "levelname": "level",
                "name": "logger",
            },
        )
    )
    handler.addFilter(CorrelationFilter())
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the correlation filter attached."""
    logger = logging.getLogger(name)
    # Ensure the filter is attached even if handlers aren't set up yet
    if not any(isinstance(f, CorrelationFilter) for f in logger.filters):
        logger.addFilter(CorrelationFilter())
    return logger
