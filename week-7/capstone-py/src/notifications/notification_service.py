"""NotificationService — Core Business Logic.

All imports are relative so the package resolves correctly whether
the project is run as  `python run.py`  or  `python -m src.run`.
"""
import os
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from .email_provider import get_email_provider
from ..utils.logger import logger

# ── In-memory stores ──────────────────────────────────────────────────────────
_notification_history: List[Dict] = []
_audit_log: List[Dict] = []
_sent_message_ids: set = set()

MAX_HISTORY = 100
MAX_AUDIT = 1000

VALID_TYPES = {"order", "welcome", "password_reset", "alert", "marketing"}
EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class NotificationService:
    """Sends notifications with retry, validation, and audit logging."""

    def __init__(
        self,
        email_provider: Optional[Callable] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
    ):
        self.email_provider = email_provider or get_email_provider()
        self.max_retries = max_retries if max_retries is not None else int(
            os.getenv("MAX_RETRY_ATTEMPTS", "3")
        )
        self.retry_delay = retry_delay if retry_delay is not None else float(
            os.getenv("RETRY_DELAY_SECONDS", "0.1")
        )

    def validate(self, payload: Dict[str, Any]) -> None:
        """Validate notification payload (REQ-004).

        Raises:
            ValueError: Descriptive validation error.
        """
        to = payload.get("to")
        subject = payload.get("subject")
        notif_type = payload.get("type")

        if not to:
            raise ValueError('Validation failed: "to" (recipient email) is required')
        if not subject:
            raise ValueError('Validation failed: "subject" is required')
        if not notif_type:
            raise ValueError('Validation failed: "type" is required')
        if not EMAIL_REGEX.match(str(to)):
            raise ValueError(f'Validation failed: "{to}" is not a valid email address')
        if notif_type not in VALID_TYPES:
            raise ValueError(
                f'Validation failed: type must be one of: {", ".join(sorted(VALID_TYPES))}'
            )

    def send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send a notification with automatic retry (REQ-001, REQ-002).

        Returns:
            Dict with success, message_id, and attempts.

        Raises:
            RuntimeError: After all retries are exhausted.
        """
        self.validate(payload)

        to = payload["to"]
        subject = payload["subject"]
        notif_type = payload["type"]
        body = payload.get("body") or self._generate_body(notif_type, to)

        retry_history: List[Dict] = []
        last_error: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                result = self.email_provider(to, subject, body, notif_type)
                message_id = result["message_id"]

                if message_id in _sent_message_ids:
                    raise RuntimeError(
                        f"Duplicate notification prevented: {message_id} already sent"
                    )
                _sent_message_ids.add(message_id)

                self._audit(to=to, subject=subject, notif_type=notif_type,
                            status="success", message_id=message_id, attempt_count=attempt)
                self._record_history(to=to, subject=subject, notif_type=notif_type,
                                     status="success", message_id=message_id)

                logger.info("Notification sent successfully",
                            to=to, notif_type=notif_type, attempt=attempt,
                            message_id=message_id)
                return {"success": True, "message_id": message_id, "attempts": attempt}

            except Exception as exc:
                last_error = exc
                retry_history.append({
                    "attempt": attempt,
                    "error": str(exc),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                logger.warning(f"Notification attempt {attempt} failed",
                               to=to, notif_type=notif_type, error=str(exc))
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * (2 ** (attempt - 1)))

        self._audit(to=to, subject=subject, notif_type=notif_type,
                    status="failed", attempt_count=self.max_retries, error=str(last_error))
        self._record_history(to=to, subject=subject, notif_type=notif_type,
                             status="failed", error=str(last_error))

        err = RuntimeError(
            f"Notification failed after {self.max_retries} attempts: {last_error}"
        )
        err.retry_history = retry_history  # type: ignore[attr-defined]
        raise err

    def get_history(self, status: Optional[str] = None) -> List[Dict]:
        """Return notification history, optionally filtered by status."""
        records = list(_notification_history)
        if status:
            records = [r for r in records if r["status"] == status]
        return records

    def get_audit_log(self) -> List[Dict]:
        """Return the governance audit log."""
        return list(_audit_log)

    def get_stats(self) -> Dict[str, Any]:
        """Return stats: total, by_type, by_status, last_sent (REQ-007)."""
        history = list(_notification_history)
        by_type: Dict[str, int] = {}
        by_status: Dict[str, int] = {}
        last_sent: Optional[str] = None

        for record in history:
            t = record.get("notif_type") or record.get("type") or "unknown"
            s = record.get("status", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
            by_status[s] = by_status.get(s, 0) + 1
            if last_sent is None or record["timestamp"] > last_sent:
                last_sent = record["timestamp"]

        return {"total": len(history), "by_type": by_type,
                "by_status": by_status, "last_sent": last_sent}

    @staticmethod
    def reset() -> None:
        """Clear all in-memory stores. Used between tests."""
        _notification_history.clear()
        _audit_log.clear()
        _sent_message_ids.clear()

    def _audit(self, **kwargs) -> None:
        _audit_log.append({"id": str(uuid.uuid4()),
                           "timestamp": datetime.now(timezone.utc).isoformat(), **kwargs})
        if len(_audit_log) > MAX_AUDIT:
            _audit_log.pop(0)

    def _record_history(self, **kwargs) -> None:
        _notification_history.append({"id": str(uuid.uuid4()),
                                      "timestamp": datetime.now(timezone.utc).isoformat(),
                                      **kwargs})
        if len(_notification_history) > MAX_HISTORY:
            _notification_history.pop(0)

    @staticmethod
    def _generate_body(notif_type: str, to: str) -> str:
        templates = {
            "order": "Your order has been confirmed. Thank you!",
            "welcome": "Welcome aboard! We are excited to have you.",
            "password_reset": "Click the link to reset your password. Expires in 1 hour.",
            "alert": "Action required: please review your account activity.",
            "marketing": "Check out our latest offers just for you!",
        }
        return templates.get(notif_type, f"Notification for {to}")
