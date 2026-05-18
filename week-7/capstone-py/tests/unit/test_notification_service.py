"""UNIT TESTS — NotificationService.

Generated via Claude Code prompt:
"Generate pytest unit tests for NotificationService covering all spec
requirements: success path, retry logic, validation, audit logging, and stats.
Inject a mock email provider so tests are deterministic and fast."

Covers: REQ-001, REQ-002, REQ-003, REQ-004, REQ-006, REQ-007
"""
import pytest

from src.notifications.notification_service import NotificationService

# ── Helpers ───────────────────────────────────────────────────────────────────

_call_count = 0


def mock_success(to, subject, body, notif_type):
    global _call_count
    _call_count += 1
    return {"message_id": f"msg-success-{_call_count}", "provider": "mock"}


def mock_failure(to, subject, body, notif_type):
    raise RuntimeError("SMTP connection refused")


def make_service(**kwargs):
    defaults = {"email_provider": mock_success, "max_retries": 3, "retry_delay": 0}
    defaults.update(kwargs)
    return NotificationService(**defaults)


VALID = {"to": "student@example.com", "subject": "Welcome", "type": "welcome"}


@pytest.fixture(autouse=True)
def reset_counter():
    global _call_count
    _call_count = 0


# ═══════════════════════════════════════════════════════
# REQ-001: Send Notification
# ═══════════════════════════════════════════════════════

class TestSendNotification:
    def test_send_returns_success_and_message_id(self):
        svc = make_service()
        result = svc.send(VALID)
        assert result["success"] is True
        assert "message_id" in result
        assert result["attempts"] == 1

    def test_provider_called_with_correct_args(self):
        calls = []

        def capturing_provider(to, subject, body, notif_type):
            calls.append({"to": to, "subject": subject, "type": notif_type})
            return {"message_id": "msg-cap-1", "provider": "mock"}

        svc = make_service(email_provider=capturing_provider)
        svc.send(VALID)
        assert calls[0]["to"] == "student@example.com"
        assert calls[0]["type"] == "welcome"

    def test_auto_generates_body_when_not_provided(self):
        calls = []

        def cap(to, subject, body, notif_type):
            calls.append(body)
            return {"message_id": "msg-body-1", "provider": "mock"}

        make_service(email_provider=cap).send(VALID)
        assert calls[0]  # body is non-empty string

    def test_uses_provided_body(self):
        calls = []

        def cap(to, subject, body, notif_type):
            calls.append(body)
            return {"message_id": "msg-body-2", "provider": "mock"}

        make_service(email_provider=cap).send({**VALID, "body": "Custom body"})
        assert calls[0] == "Custom body"


# ═══════════════════════════════════════════════════════
# REQ-002: Retry Logic
# ═══════════════════════════════════════════════════════

class TestRetryLogic:
    def test_retries_exactly_max_retries_times(self):
        call_count = [0]

        def fail(to, subject, body, notif_type):
            call_count[0] += 1
            raise RuntimeError("fail")

        svc = make_service(email_provider=fail, max_retries=3)
        with pytest.raises(RuntimeError):
            svc.send(VALID)
        assert call_count[0] == 3

    def test_succeeds_on_second_attempt(self):
        attempts = [0]

        def flaky(to, subject, body, notif_type):
            attempts[0] += 1
            if attempts[0] == 1:
                raise RuntimeError("transient")
            return {"message_id": "msg-retry-ok", "provider": "mock"}

        svc = make_service(email_provider=flaky, max_retries=3)
        result = svc.send(VALID)
        assert result["success"] is True
        assert result["attempts"] == 2

    def test_raises_with_retry_history_after_exhaustion(self):
        svc = make_service(email_provider=mock_failure, max_retries=3)
        with pytest.raises(RuntimeError) as exc_info:
            svc.send(VALID)
        assert hasattr(exc_info.value, "retry_history")
        history = exc_info.value.retry_history
        assert len(history) == 3
        assert history[0]["attempt"] == 1
        assert history[2]["attempt"] == 3

    def test_retry_history_entries_have_required_fields(self):
        svc = make_service(email_provider=mock_failure, max_retries=2)
        with pytest.raises(RuntimeError) as exc_info:
            svc.send(VALID)
        entry = exc_info.value.retry_history[0]
        assert "attempt" in entry
        assert "error" in entry
        assert "timestamp" in entry


# ═══════════════════════════════════════════════════════
# REQ-003: Audit Logging
# ═══════════════════════════════════════════════════════

class TestAuditLogging:
    def test_success_entry_written_to_audit_log(self):
        svc = make_service()
        svc.send(VALID)
        log = svc.get_audit_log()
        assert len(log) == 1
        assert log[0]["status"] == "success"
        assert log[0]["to"] == "student@example.com"

    def test_failure_entry_written_to_audit_log(self):
        svc = make_service(email_provider=mock_failure, max_retries=1)
        with pytest.raises(RuntimeError):
            svc.send(VALID)
        log = svc.get_audit_log()
        assert len(log) == 1
        assert log[0]["status"] == "failed"

    def test_audit_entry_has_required_fields(self):
        svc = make_service()
        svc.send(VALID)
        entry = svc.get_audit_log()[0]
        for field in ["id", "timestamp", "to", "notif_type", "status", "attempt_count"]:
            assert field in entry


# ═══════════════════════════════════════════════════════
# REQ-004: Input Validation
# ═══════════════════════════════════════════════════════

class TestInputValidation:
    def test_missing_to_raises_value_error(self):
        svc = make_service()
        with pytest.raises(ValueError, match="to"):
            svc.send({"subject": "Hi", "type": "welcome"})

    def test_missing_subject_raises_value_error(self):
        svc = make_service()
        with pytest.raises(ValueError, match="subject"):
            svc.send({"to": "user@test.com", "type": "welcome"})

    def test_missing_type_raises_value_error(self):
        svc = make_service()
        with pytest.raises(ValueError, match="type"):
            svc.send({"to": "user@test.com", "subject": "Hi"})

    def test_invalid_email_format(self):
        svc = make_service()
        with pytest.raises(ValueError, match="valid email"):
            svc.send({"to": "not-an-email", "subject": "Hi", "type": "welcome"})

    def test_invalid_type(self):
        svc = make_service()
        with pytest.raises(ValueError, match="must be one of"):
            svc.send({"to": "u@test.com", "subject": "Hi", "type": "INVALID"})

    @pytest.mark.parametrize("t", ["order", "welcome", "password_reset", "alert", "marketing"])
    def test_all_valid_types_accepted(self, t):
        counter = [0]

        def prov(to, subject, body, notif_type):
            counter[0] += 1
            return {"message_id": f"msg-{t}-{counter[0]}", "provider": "mock"}

        NotificationService.reset()
        svc = make_service(email_provider=prov)
        result = svc.send({"to": "u@test.com", "subject": "T", "type": t})
        assert result["success"] is True


# ═══════════════════════════════════════════════════════
# REQ-006: Notification History
# ═══════════════════════════════════════════════════════

class TestNotificationHistory:
    def test_history_recorded_after_success(self):
        svc = make_service()
        svc.send(VALID)
        history = svc.get_history()
        assert len(history) == 1
        assert history[0]["to"] == "student@example.com"
        assert history[0]["status"] == "success"

    def test_history_filter_by_status(self):
        svc = make_service()
        svc.send(VALID)
        fail_svc = make_service(email_provider=mock_failure, max_retries=1)
        with pytest.raises(RuntimeError):
            fail_svc.send({"to": "x@test.com", "subject": "F", "type": "alert"})

        successes = svc.get_history(status="success")
        assert all(r["status"] == "success" for r in successes)


# ═══════════════════════════════════════════════════════
# REQ-007: Stats
# ═══════════════════════════════════════════════════════

class TestStats:
    def test_stats_empty_on_start(self):
        svc = make_service()
        s = svc.get_stats()
        assert s["total"] == 0
        assert s["by_type"] == {}
        assert s["by_status"] == {}
        assert s["last_sent"] is None

    def test_total_increments_after_send(self):
        svc = make_service()
        svc.send(VALID)
        assert svc.get_stats()["total"] == 1

    def test_by_type_groups_correctly(self):
        counter = [0]

        def prov(to, subject, body, notif_type):
            counter[0] += 1
            return {"message_id": f"msg-type-{counter[0]}", "provider": "mock"}

        svc = make_service(email_provider=prov)
        svc.send({"to": "a@test.com", "subject": "A", "type": "order"})
        svc.send({"to": "b@test.com", "subject": "B", "type": "order"})
        svc.send({"to": "c@test.com", "subject": "C", "type": "welcome"})
        stats = svc.get_stats()
        assert stats["by_type"]["order"] == 2
        assert stats["by_type"]["welcome"] == 1

    def test_by_status_groups_correctly(self):
        svc = make_service()
        svc.send(VALID)
        fail_svc = make_service(email_provider=mock_failure, max_retries=1)
        with pytest.raises(RuntimeError):
            fail_svc.send({"to": "x@test.com", "subject": "F", "type": "alert"})

        stats = svc.get_stats()
        assert stats["by_status"].get("success", 0) >= 1

    def test_last_sent_is_timestamp(self):
        svc = make_service()
        svc.send(VALID)
        stats = svc.get_stats()
        assert stats["last_sent"] is not None
        assert "T" in stats["last_sent"]  # ISO timestamp
