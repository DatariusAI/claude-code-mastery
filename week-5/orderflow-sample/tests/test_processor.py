"""
tests/test_processor.py
Existing unit tests for payments/processor.py — intentionally sparse.
Students will use the Test Agent to identify coverage gaps.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from payments.processor import process_payment, refund_payment


class TestProcessPayment:
    """Basic happy-path tests only — many edge cases missing."""

    @patch("payments.processor._call_stripe_api")
    @patch("payments.processor._execute_query")
    def test_successful_payment(self, mock_db, mock_stripe):
        """Test a basic successful payment."""
        mock_stripe.return_value = {"id": "ch_test_123"}

        result = process_payment(
            amount=1000,
            currency="usd",
            card_token="tok_visa",
            user_id="user_001"
        )

        assert result["success"] is True
        assert result["charge_id"] == "ch_test_123"
        assert result["error"] is None

    @patch("payments.processor._call_stripe_api")
    @patch("payments.processor._execute_query")
    def test_payment_retries_on_failure(self, mock_db, mock_stripe):
        """Test that payment retries on exception."""
        mock_stripe.side_effect = [Exception("Network error"), {"id": "ch_retry_456"}]

        result = process_payment(1000, "usd", "tok_visa", "user_001")

        assert result["success"] is True
        assert mock_stripe.call_count == 2

    # MISSING: test for negative amount
    # MISSING: test for zero amount
    # MISSING: test for None card_token
    # MISSING: test for invalid currency
    # MISSING: test for all retries exhausted
    # MISSING: test for record_transaction called with correct args


class TestRefundPayment:

    @patch("payments.processor._call_stripe_api")
    def test_full_refund(self, mock_stripe):
        """Test a full refund."""
        mock_stripe.return_value = {"id": "re_test_789"}
        result = refund_payment("ch_test_123")
        assert result["id"] == "re_test_789"

    # MISSING: test partial refund
    # MISSING: test refund with invalid charge_id
    # MISSING: test authorization — any user can refund any charge
