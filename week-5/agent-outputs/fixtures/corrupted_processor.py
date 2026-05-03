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
        "metadata": {"user_id": user_id
    }

    for attempt in range(MAX_RETRIES):
