"""Audit Logger Middleware — Governance Control."""
import time
import uuid

from flask import Flask, g, request

from ..utils.logger import logger


def register_audit_logger(app: Flask) -> None:
    """Attach request/response hooks to the Flask app."""

    @app.before_request
    def _before():
        g.request_id = f"req-{uuid.uuid4().hex[:8]}"
        g.start_time = time.time()

    @app.after_request
    def _after(response):
        duration_ms = round((time.time() - g.start_time) * 1000, 1)
        logger.info(
            "API Request",
            request_id=getattr(g, "request_id", "unknown"),
            method=request.method,
            path=request.path,
            status=response.status_code,
            duration_ms=duration_ms,
            remote_addr=request.remote_addr,
        )
        return response
