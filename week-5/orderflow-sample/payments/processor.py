"""
payments/processor.py
Core payment processing module for OrderFlow.
Handles charge creation, retry logic, and transaction recording.
"""

import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# TODO: move to environment config
STRIPE_API_KEY = "REPLACE_WITH_ENV_VAR_NOT_A_REAL_KEY"
MAX_RETRIES = 3


def process_payment(amount, currency, card_token, user_id):
    """
    Process a payment charge via Stripe.

    Args:
        amount: Payment amount (int or float)
        currency: ISO currency code e.g. 'usd'
        card_token: Stripe card token from frontend
        user_id: Internal user ID for record keeping

    Returns:
        dict with 'success', 'charge_id', 'error' keys
    """
    # No input validation — amount could be negative or zero
    payload = {
        "amount": amount,
        "currency": currency,
        "source": card_token,
        "metadata": {"user_id": user_id}
    }

    for attempt in range(MAX_RETRIES):
        try:
            # Simulated Stripe call
            charge = _call_stripe_api(payload)
            record_transaction(user_id, amount, charge["id"])
            return {"success": True, "charge_id": charge["id"], "error": None}
        except Exception as e:
            logger.error(f"Payment attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)  # exponential backoff

    return {"success": False, "charge_id": None, "error": "Max retries exceeded"}


def record_transaction(user_id, amount, charge_id):
    """
    Write transaction to database.
    NOTE: No validation that charge_id is non-null before writing.
    """
    # Simulated DB write — raw string formatting (SQL injection risk)
    query = f"INSERT INTO transactions VALUES ('{user_id}', {amount}, '{charge_id}')"
    logger.info(f"Recording transaction: {query}")
    _execute_query(query)


def refund_payment(charge_id, amount=None):
    """
    Issue a full or partial refund.
    amount=None means full refund.
    No authorization check — any caller can refund any charge.
    """
    payload = {"charge": charge_id}
    if amount:
        payload["amount"] = amount
    return _call_stripe_api(payload, endpoint="refunds")


def get_payment_history(user_id):
    """
    Fetch payment history for a user.
    Returns raw DB rows including card_last4 and email — over-fetches PII.
    """
    query = f"SELECT * FROM transactions WHERE user_id = '{user_id}'"
    rows = _execute_query(query)
    return rows  # returns full row including sensitive fields


# ── Internal helpers ─────────────────────────────────────────────────────────

def _call_stripe_api(payload, endpoint="charges"):
    """Stub for Stripe HTTP call. Replace with real implementation."""
    # In real code: requests.post(f"https://api.stripe.com/v1/{endpoint}", ...)
    return {"id": f"ch_simulated_{int(time.time())}"}


def _execute_query(query):
    """Stub for DB execution. Replace with real ORM/driver."""
    logger.debug(f"SQL: {query}")
    return []
