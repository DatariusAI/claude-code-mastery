"""
Integration tests for the two workflows. Three tests with unittest.mock
so no real MCP calls happen.

Run with: pytest tests/test_workflows.py
"""
import json
import pytest
from unittest.mock import MagicMock, patch
from workflows.morning_brief import MorningBriefWorkflow
from workflows.incident_triage import (IncidentTriageWorkflow,
                                       ESCALATE_FALLBACK)


def _make_config():
    cfg = MagicMock()
    cfg.GITHUB_REPO = "instructor/fintrack-backend-lab"
    cfg.CLAUDE_MODEL = "claude-sonnet-4-20250514"
    return cfg


def test_morning_brief_structure():
    """Output contains all 4 required section headers."""
    mock_mcp = MagicMock()
    expected_response = (
        "## PRs_NEEDING_REVIEW\n- PR #42\n\n"
        "## OPEN_P0_P1\n- Issue #100\n\n"
        "## OVERNIGHT_DB_ALERTS\nNo data returned from "
        "db_overnight_alerts\n\n"
        "## ACTION_ITEMS\n- Review PR #42\n- Triage Issue #100\n"
        "- Monitor DB\n"
    )
    mock_mcp.ask.return_value = expected_response

    with patch("workflows.morning_brief.github_tools.get_open_prs",
               return_value=[{"number": 42, "title": "x",
                              "author": "a", "days_open": 2,
                              "review_count": 0}]), \
         patch("workflows.morning_brief.github_tools."
               "get_priority_issues",
               return_value=[{"number": 100, "title": "y",
                              "priority": "P0", "assignee": "b",
                              "days_open": 1}]), \
         patch("workflows.morning_brief.db_tools."
               "get_overnight_alerts", return_value=[]):
        wf = MorningBriefWorkflow(mcp=mock_mcp,
                                  config=_make_config())
        result = wf.execute()

    for header in ["## PRs_NEEDING_REVIEW", "## OPEN_P0_P1",
                   "## OVERNIGHT_DB_ALERTS", "## ACTION_ITEMS"]:
        assert header in result, f"Missing header: {header}"


def test_incident_triage_valid_json():
    """Returned dict has all 7 keys with correct types."""
    mock_mcp = MagicMock()
    valid_payload = {
        "service": "payments",
        "error_rate_now": 0.45,
        "error_rate_30min_avg": 0.12,
        "likely_cause": "Recent deploy regressed retry logic",
        "recent_deploys": ["abc1234: fix retry",
                           "def5678: bump dep"],
        "recommended_action": "Rollback abc1234 and rerun "
                              "integration tests",
        "escalate": True,
    }
    mock_mcp.ask.return_value = json.dumps(valid_payload)

    with patch("workflows.incident_triage.db_tools.get_error_rate",
               return_value={"service": "payments",
                             "window_minutes": 30,
                             "error_rate": 0.12, "baseline": 0.1,
                             "requests_total": 1000,
                             "errors_total": 120,
                             "as_of": "2026-04-26T12:00:00Z"}), \
         patch("workflows.incident_triage.github_tools."
               "search_recent_commits", return_value=[]), \
         patch("workflows.incident_triage.github_tools."
               "get_priority_issues", return_value=[]):
        wf = IncidentTriageWorkflow(mcp=mock_mcp,
                                    config=_make_config())
        result = wf.execute(service_name="payments")

    expected_keys = {"service", "error_rate_now",
                     "error_rate_30min_avg", "likely_cause",
                     "recent_deploys", "recommended_action",
                     "escalate"}
    assert expected_keys.issubset(result.keys())
    assert isinstance(result["service"], str)
    assert isinstance(result["error_rate_now"], (int, float))
    assert isinstance(result["error_rate_30min_avg"], (int, float))
    assert isinstance(result["likely_cause"], str)
    assert isinstance(result["recent_deploys"], list)
    assert isinstance(result["recommended_action"], str)
    assert isinstance(result["escalate"], bool)


def test_incident_triage_degraded():
    """First db_tools call raises; workflow returns escalate=True
    fallback without raising."""
    mock_mcp = MagicMock()
    mock_mcp.ask.return_value = "not valid json {{{"

    call_count = {"n": 0}
    def flaky_get_error_rate(*args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise RuntimeError("DB unavailable")
        return {"service": "payments", "window_minutes": 5,
                "error_rate": 0.5, "baseline": 0.1,
                "requests_total": 1000, "errors_total": 500,
                "as_of": "2026-04-26T12:00:00Z"}

    with patch("workflows.incident_triage.db_tools.get_error_rate",
               side_effect=flaky_get_error_rate), \
         patch("workflows.incident_triage.github_tools."
               "search_recent_commits", return_value=[]), \
         patch("workflows.incident_triage.github_tools."
               "get_priority_issues", return_value=[]):
        wf = IncidentTriageWorkflow(mcp=mock_mcp,
                                    config=_make_config())
        result = wf.execute(service_name="payments")  # MUST NOT raise

    assert result["escalate"] is True
    assert result["service"] == "payments"
