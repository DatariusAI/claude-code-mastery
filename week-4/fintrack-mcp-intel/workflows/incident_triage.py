"""
Incident Triage Workflow (WF-02).

Triggered during a live incident. Chains 4 MCP calls to diagnose
the probable cause and recommend an action.

Output: A JSON dict matching the IncidentReport schema below.
"""
from __future__ import annotations
import json
import sys
from typing import TypedDict

from mcp import github_tools, db_tools
from workflows.base import BaseWorkflow


class IncidentReport(TypedDict):
    """The exact JSON schema your workflow must return."""
    service:             str
    error_rate_now:      float
    error_rate_30min_avg: float
    likely_cause:        str
    recent_deploys:      list[str]
    recommended_action:  str
    escalate:            bool


# Fallback returned when parsing fails or a critical error occurs
ESCALATE_FALLBACK: IncidentReport = {
    "service":              "unknown",
    "error_rate_now":       -1.0,
    "error_rate_30min_avg": -1.0,
    "likely_cause":         "Triage workflow failed — see stderr for details",
    "recent_deploys":       [],
    "recommended_action":   "Page on-call immediately — automated triage unavailable",
    "escalate":             True,
}

REQUIRED_KEYS = {
    "service", "error_rate_now", "error_rate_30min_avg",
    "likely_cause", "recent_deploys", "recommended_action", "escalate",
}


class IncidentTriageWorkflow(BaseWorkflow):
    name = "incident_triage"

    def execute(self, service_name: str = "payments") -> IncidentReport:
        try:
            data_30min = db_tools.get_error_rate(service_name, window_minutes=30)
        except Exception as exc:
            print(f"incident_triage step failed: {exc}", file=sys.stderr)
            data_30min = {}

        try:
            data_commits = github_tools.search_recent_commits(
                self.mcp, self.config.GITHUB_REPO, service_name, hours=4
            )
        except Exception as exc:
            print(f"incident_triage step failed: {exc}", file=sys.stderr)
            data_commits = []

        try:
            data_bugs = github_tools.get_priority_issues(
                self.mcp, self.config.GITHUB_REPO,
                labels=["bug", service_name],
            )
        except Exception as exc:
            print(f"incident_triage step failed: {exc}", file=sys.stderr)
            data_bugs = []

        try:
            data_now = db_tools.get_error_rate(service_name, window_minutes=5)
        except Exception as exc:
            print(f"incident_triage step failed: {exc}", file=sys.stderr)
            data_now = {}

        prompt_tpl = self._load_prompt("incident_triage.txt")
        prompt = (
            prompt_tpl
            .replace("{{SERVICE_NAME}}", service_name)
            .replace("{{ERROR_RATE_30MIN}}", json.dumps(data_30min, indent=2))
            .replace("{{ERROR_RATE_NOW}}", json.dumps(data_now, indent=2))
            .replace("{{RECENT_COMMITS}}", json.dumps(data_commits, indent=2))
            .replace("{{OPEN_BUGS}}", json.dumps(data_bugs, indent=2))
        )

        raw = self.mcp.ask(prompt)

        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = "\n".join(cleaned.splitlines()[1:])
            if cleaned.rstrip().endswith("```"):
                cleaned = cleaned.rstrip()[:-3]
        cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            print(
                f"incident_triage: malformed JSON. Raw: {raw}",
                file=sys.stderr,
            )
            fallback = dict(ESCALATE_FALLBACK)
            fallback["service"] = service_name
            return fallback

        if not isinstance(parsed, dict) or not REQUIRED_KEYS.issubset(parsed.keys()):
            print(
                f"incident_triage: response missing required keys. Got: {parsed}",
                file=sys.stderr,
            )
            fallback = dict(ESCALATE_FALLBACK)
            fallback["service"] = service_name
            return fallback

        return parsed
