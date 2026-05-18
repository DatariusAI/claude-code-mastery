"""INTEGRATION TESTS — Notification Service REST API.

Generated via Claude Code prompt:
"Generate pytest + Flask test client integration tests for all API
endpoints. Cover success paths, validation errors, filtering, and
health check."
"""
import pytest


VALID = {"to": "user@example.com", "subject": "Order Confirmed", "type": "order"}


# ═══════════════════════════════════════════════════════
# GET /api/health
# ═══════════════════════════════════════════════════════

class TestHealth:
    def test_returns_200_with_status_ok(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        data = r.get_json()
        assert data["status"] == "ok"

    def test_includes_uptime(self, client):
        r = client.get("/api/health")
        assert isinstance(r.get_json()["uptime"], (int, float))

    def test_includes_version(self, client):
        r = client.get("/api/health")
        assert "version" in r.get_json()

    def test_responds_quickly(self, client):
        import time
        start = time.time()
        client.get("/api/health")
        assert (time.time() - start) < 0.2


# ═══════════════════════════════════════════════════════
# POST /api/notifications/send
# ═══════════════════════════════════════════════════════

class TestSendNotification:
    def test_returns_200_with_message_id(self, client):
        r = client.post("/api/notifications/send",
                        json=VALID, content_type="application/json")
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert "message_id" in data

    def test_returns_400_missing_to(self, client):
        r = client.post("/api/notifications/send",
                        json={"subject": "Hi", "type": "welcome"})
        assert r.status_code == 400
        assert "to" in r.get_json()["error"].lower()

    def test_returns_400_missing_subject(self, client):
        r = client.post("/api/notifications/send",
                        json={"to": "u@test.com", "type": "welcome"})
        assert r.status_code == 400
        assert "subject" in r.get_json()["error"].lower()

    def test_returns_400_missing_type(self, client):
        r = client.post("/api/notifications/send",
                        json={"to": "u@test.com", "subject": "Hi"})
        assert r.status_code == 400
        assert "type" in r.get_json()["error"].lower()

    def test_returns_400_invalid_email(self, client):
        r = client.post("/api/notifications/send",
                        json={"to": "not-an-email", "subject": "Hi", "type": "welcome"})
        assert r.status_code == 400
        assert "valid email" in r.get_json()["error"].lower()

    def test_returns_400_invalid_type(self, client):
        r = client.post("/api/notifications/send",
                        json={"to": "u@test.com", "subject": "Hi", "type": "UNKNOWN"})
        assert r.status_code == 400

    def test_returns_500_with_retry_history_on_failure(self, client):
        r = client.post("/api/notifications/send",
                        json={"to": "fail@test.com", "subject": "F", "type": "alert"})
        assert r.status_code == 500
        data = r.get_json()
        assert data["success"] is False
        assert "retry_history" in data
        assert isinstance(data["retry_history"], list)

    @pytest.mark.parametrize("t", ["order", "welcome", "password_reset", "alert", "marketing"])
    def test_all_valid_types_accepted(self, client, t):
        r = client.post("/api/notifications/send",
                        json={"to": f"u+{t}@example.com", "subject": "T", "type": t})
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════
# GET /api/notifications
# ═══════════════════════════════════════════════════════

class TestNotificationHistory:
    def test_empty_list_initially(self, client):
        r = client.get("/api/notifications")
        assert r.status_code == 200
        data = r.get_json()
        assert data["notifications"] == []
        assert data["count"] == 0

    def test_populated_after_send(self, client):
        client.post("/api/notifications/send", json=VALID)
        r = client.get("/api/notifications")
        assert r.get_json()["count"] == 1

    def test_filter_by_status_success(self, client):
        client.post("/api/notifications/send", json=VALID)
        client.post("/api/notifications/send",
                    json={"to": "fail@test.com", "subject": "F", "type": "alert"})
        r = client.get("/api/notifications?status=success")
        records = r.get_json()["notifications"]
        assert all(rec["status"] == "success" for rec in records)

    def test_filter_by_status_failed(self, client):
        client.post("/api/notifications/send",
                    json={"to": "fail@test.com", "subject": "F", "type": "alert"})
        r = client.get("/api/notifications?status=failed")
        records = r.get_json()["notifications"]
        assert all(rec["status"] == "failed" for rec in records)

    def test_record_has_required_fields(self, client):
        client.post("/api/notifications/send", json=VALID)
        record = client.get("/api/notifications").get_json()["notifications"][0]
        for field in ["id", "to", "subject", "status", "timestamp"]:
            assert field in record


# ═══════════════════════════════════════════════════════
# GET /api/notifications/audit
# ═══════════════════════════════════════════════════════

class TestAuditLog:
    def test_empty_initially(self, client):
        r = client.get("/api/notifications/audit")
        assert r.status_code == 200
        assert r.get_json()["audit_log"] == []

    def test_populated_after_send(self, client):
        client.post("/api/notifications/send", json=VALID)
        r = client.get("/api/notifications/audit")
        assert r.get_json()["count"] == 1

    def test_failed_sends_appear_in_audit(self, client):
        client.post("/api/notifications/send",
                    json={"to": "fail@test.com", "subject": "F", "type": "alert"})
        log = client.get("/api/notifications/audit").get_json()["audit_log"]
        assert log[0]["status"] == "failed"


# ═══════════════════════════════════════════════════════
# GET /api/notifications/stats
# ═══════════════════════════════════════════════════════

class TestStats:
    def test_returns_200_with_correct_shape(self, client):
        r = client.get("/api/notifications/stats")
        assert r.status_code == 200
        data = r.get_json()
        assert "total" in data
        assert "by_type" in data
        assert "by_status" in data
        assert "last_sent" in data

    def test_total_zero_initially(self, client):
        assert client.get("/api/notifications/stats").get_json()["total"] == 0

    def test_total_increments_after_send(self, client):
        client.post("/api/notifications/send", json=VALID)
        assert client.get("/api/notifications/stats").get_json()["total"] == 1

    def test_by_type_breakdown(self, client):
        client.post("/api/notifications/send", json=VALID)  # order
        client.post("/api/notifications/send",
                    json={"to": "b@test.com", "subject": "W", "type": "welcome"})
        stats = client.get("/api/notifications/stats").get_json()
        assert stats["by_type"].get("order", 0) >= 1
        assert stats["by_type"].get("welcome", 0) >= 1

    def test_by_status_separates_success_and_failed(self, client):
        client.post("/api/notifications/send", json=VALID)
        client.post("/api/notifications/send",
                    json={"to": "fail@test.com", "subject": "F", "type": "alert"})
        stats = client.get("/api/notifications/stats").get_json()
        assert stats["by_status"].get("success", 0) >= 1
        assert stats["by_status"].get("failed", 0) >= 1


# ═══════════════════════════════════════════════════════
# 404 / unknown routes
# ═══════════════════════════════════════════════════════

class TestUnknownRoutes:
    def test_unknown_route_returns_404(self, client):
        assert client.get("/unknown-route").status_code == 404
