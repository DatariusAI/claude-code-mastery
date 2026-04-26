"""
Morning Intelligence Brief Workflow (WF-01).

This workflow runs every morning and gives the FinTrack engineering team
a concise, data-driven overview of what needs attention.

Data sources:
  - GitHub: open PRs needing review, open P0/P1 issues
  - PostgreSQL: services with elevated error rates overnight

Output: A markdown string with 4 required sections.
"""
from __future__ import annotations
import json

from mcp import github_tools, db_tools
from workflows.base import BaseWorkflow


class MorningBriefWorkflow(BaseWorkflow):
    name = "morning_brief"

    def execute(self) -> str:
        data_prs = github_tools.get_open_prs(self.mcp, self.config.GITHUB_REPO)
        data_issues = github_tools.get_priority_issues(
            self.mcp, self.config.GITHUB_REPO
        )
        data_alerts = db_tools.get_overnight_alerts()

        prompt_tpl = self._load_prompt("morning_brief.txt")
        prompt = (
            prompt_tpl
            .replace("{{PR_DATA}}", json.dumps(data_prs, indent=2))
            .replace("{{ISSUE_DATA}}", json.dumps(data_issues, indent=2))
            .replace("{{DB_ALERTS}}", json.dumps(data_alerts, indent=2))
        )

        result = self.mcp.ask(prompt)
        return result
