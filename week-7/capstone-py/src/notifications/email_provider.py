"""Email Provider Adapter.

Uses relative imports so the package works when run from the project root
as  `python run.py`  or  `python -m src.run`.
"""
import os
import uuid
from typing import Dict

from ..utils.logger import logger


def mock_email_provider(to: str, subject: str, body: str, notif_type: str) -> Dict[str, str]:
    """Simulate email delivery (mock).

    Raises RuntimeError for fail@test.com to exercise retry logic.
    """
    if to == "fail@test.com":
        raise RuntimeError("SMTP connection refused: mock provider error")

    message_id = f"mock-{uuid.uuid4()}"
    logger.info("Email sent via mock provider",
                to=to, subject=subject, notif_type=notif_type, message_id=message_id)
    return {"message_id": message_id, "provider": "mock"}


def smtp_email_provider(to: str, subject: str, body: str, notif_type: str) -> Dict[str, str]:
    """Send via real SMTP (production). Falls back to mock if unconfigured."""
    logger.warning("SMTP provider not configured — falling back to mock", to=to)
    return mock_email_provider(to, subject, body, notif_type)


def get_email_provider():
    """Return active email provider based on EMAIL_PROVIDER env var."""
    name = os.getenv("EMAIL_PROVIDER", "mock")
    return smtp_email_provider if name == "smtp" else mock_email_provider
