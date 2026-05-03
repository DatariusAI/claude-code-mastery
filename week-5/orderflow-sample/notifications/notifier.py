"""
notifications/notifier.py
Email and SMS notification service for OrderFlow.
Sends transactional messages on payment events.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# SMTP credentials — should be env vars
SMTP_HOST = "smtp.mailprovider.com"
SMTP_USER = "noreply@orderflow.com"
SMTP_PASSWORD = "REPLACE_WITH_ENV_VAR_NOT_A_REAL_PASSWORD"


def send_payment_confirmation(user_email: str, amount: float, charge_id: str) -> bool:
    """
    Send a payment confirmation email.

    Args:
        user_email: Recipient email address
        amount: Payment amount in dollars
        charge_id: Stripe charge ID

    Returns:
        True if sent successfully
    """
    subject = "Payment Confirmed — OrderFlow"
    # Amount not formatted — could expose float precision issues
    body = f"Your payment of ${amount} has been confirmed. Reference: {charge_id}"

    return _send_email(user_email, subject, body)


def send_payment_failure(user_email: str, amount: float, reason: str) -> bool:
    """Send a payment failure notification."""
    subject = "Payment Failed — OrderFlow"
    # Reason string passed directly from Stripe — could contain internal error details
    body = f"Your payment of ${amount} failed. Reason: {reason}. Please update your payment method."
    return _send_email(user_email, subject, body)


def send_refund_confirmation(user_email: str, amount: float) -> bool:
    """Send a refund confirmation."""
    subject = "Refund Processed — OrderFlow"
    body = f"Your refund of ${amount} has been processed and will appear in 5–10 business days."
    return _send_email(user_email, subject, body)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _send_email(to: str, subject: str, body: str) -> bool:
    """
    Send an email via SMTP.
    No rate limiting — can be called in a loop without restriction.
    No input sanitisation on 'to' address.
    """
    logger.info(f"Sending email to {to}: [{subject}]")
    # Stub — in real code: smtplib.SMTP(SMTP_HOST).sendmail(...)
    return True
