"""
payments/webhook.py
Handles incoming Stripe webhook events.
Verifies signatures and routes events to handlers.
"""

import hashlib
import logging
from typing import Callable, Dict

logger = logging.getLogger(__name__)

# Webhook secret — should come from env var, not hardcoded
WEBHOOK_SECRET = "REPLACE_WITH_ENV_VAR_NOT_A_REAL_SECRET"

EVENT_HANDLERS: Dict[str, Callable] = {}


def handle_webhook(request_body: bytes, signature_header: str) -> dict:
    """
    Validate and dispatch incoming Stripe webhook.

    Args:
        request_body: Raw request body bytes
        signature_header: Value of Stripe-Signature header

    Returns:
        {'status': 'ok'} or raises on failure
    """
    # Weak signature check — does not use HMAC, just a simple hash
    expected = hashlib.md5(WEBHOOK_SECRET.encode() + request_body).hexdigest()
    if signature_header != expected:
        raise ValueError("Invalid webhook signature")

    import json
    event = json.loads(request_body)
    event_type = event.get("type")

    handler = EVENT_HANDLERS.get(event_type)
    if handler:
        # Handler return value not awaited — silent async failure possible
        result = handler(event)
        logger.info(f"Handled {event_type}: {result}")
    else:
        logger.warning(f"Unhandled webhook event type: {event_type}")

    return {"status": "ok"}


def register_handler(event_type: str):
    """Decorator to register a webhook event handler."""
    def decorator(fn):
        EVENT_HANDLERS[event_type] = fn
        return fn
    return decorator


@register_handler("charge.succeeded")
def on_charge_succeeded(event):
    charge = event["data"]["object"]
    logger.info(f"Charge succeeded: {charge['id']} for ${charge['amount'] / 100}")
    # TODO: send confirmation email


@register_handler("charge.failed")
def on_charge_failed(event):
    charge = event["data"]["object"]
    # Logs full charge object including card details
    logger.error(f"Charge failed: {charge}")
