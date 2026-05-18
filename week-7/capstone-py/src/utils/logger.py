"""Structured JSON logger utility."""
import json
import os
import sys
from datetime import datetime, timezone


def _json_record(level: str, message: str, **kwargs) -> str:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "message": message,
    }
    entry.update(kwargs)
    return json.dumps(entry)


class StructuredLogger:
    """Emits structured JSON log lines to stdout/stderr."""

    LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}

    def __init__(self, name: str = "app"):
        self.name = name
        raw = os.getenv("LOG_LEVEL", "INFO").upper()
        self._level = self.LEVELS.get(raw, 20)

    def debug(self, message: str, **kwargs):
        if self._level <= 10:
            print(_json_record("DEBUG", message, **kwargs), file=sys.stdout)

    def info(self, message: str, **kwargs):
        if self._level <= 20:
            print(_json_record("INFO", message, **kwargs), file=sys.stdout)

    def warning(self, message: str, **kwargs):
        if self._level <= 30:
            print(_json_record("WARNING", message, **kwargs), file=sys.stdout)

    def error(self, message: str, **kwargs):
        if self._level <= 40:
            print(_json_record("ERROR", message, **kwargs), file=sys.stderr)


logger = StructuredLogger("notification-service")
