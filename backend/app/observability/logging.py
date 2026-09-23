"""
Structured JSON logging configuration.

Phase 1 provides basic structured logs to stdout. Full OpenTelemetry
tracing/metrics is implemented in Phase 10 — this module is intentionally
lightweight for now and is the extension point for that later work.
"""

import json
import logging
import sys
from datetime import UTC, datetime


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "service": "nexus-backend",
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        # Allow callers to attach extra structured fields via `extra={...}`
        for key, value in record.__dict__.items():
            if key in (
                "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
                "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
                "created", "msecs", "relativeCreated", "thread", "threadName",
                "processName", "process", "message",
            ):
                continue
            payload[key] = value
        return json.dumps(payload, default=str)


def configure_logging(log_level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level.upper())

    # Quiet noisy third-party loggers at DEBUG level
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
