"""Notification Routes — REST API Blueprint."""
import time
from typing import Tuple

from flask import Blueprint, jsonify, request

from ..notifications.notification_service import NotificationService
from ..utils.logger import logger

bp = Blueprint("notifications", __name__, url_prefix="/api")
_service = NotificationService()
_START_TIME = time.time()


@bp.route("/health")
def health():
    """Return service health status (REQ-005)."""
    import os
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "uptime": round(time.time() - _START_TIME),
        "environment": os.getenv("FLASK_ENV", "production"),
    })


@bp.route("/notifications/send", methods=["POST"])
def send_notification() -> Tuple:
    """Send a notification (REQ-001, REQ-002, REQ-004)."""
    data = request.get_json(silent=True) or {}
    try:
        result = _service.send(data)
        return jsonify(result), 200
    except ValueError as exc:
        logger.error(str(exc), path=request.path)
        return jsonify({"success": False, "error": str(exc)}), 400
    except RuntimeError as exc:
        logger.error(str(exc), path=request.path)
        response = {"success": False, "error": str(exc)}
        if hasattr(exc, "retry_history"):
            response["retry_history"] = exc.retry_history  # type: ignore[attr-defined]
        return jsonify(response), 500


@bp.route("/notifications")
def notification_history():
    """Return notification history, filtered by ?status= (REQ-006)."""
    status = request.args.get("status")
    records = _service.get_history(status=status)
    return jsonify({"count": len(records), "notifications": records})


@bp.route("/notifications/audit")
def audit_log():
    """Return the governance audit log (REQ-003)."""
    log = _service.get_audit_log()
    return jsonify({"count": len(log), "audit_log": log})


@bp.route("/notifications/stats")
def stats():
    """Return notification statistics summary (REQ-007)."""
    return jsonify(_service.get_stats())
