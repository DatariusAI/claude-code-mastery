"""
GitHub MCP Tool Wrappers.

Each function wraps one or more GitHub MCP tool calls, handles errors
gracefully (returning [] on failure), and logs every call via AuditLogger.

The caller (workflow code) should never see an exception from this module.
"""
from __future__ import annotations
import sys
import time
from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING

from mcp.audit import AuditLogger

if TYPE_CHECKING:
    from mcp.client import MCPClient


_audit = AuditLogger()


def get_open_prs(mcp: "MCPClient", repo: str, min_age_days: int = 1) -> list[dict]:
    """
    Fetch open, non-draft pull requests older than min_age_days.

    Returns list of dicts: number, title, author, days_open, review_count.
    Returns [] on any error.
    """
    tool_name = "github_pull_requests"
    tool_input = {"repo": repo, "state": "open"}
    start = time.perf_counter()
    try:
        raw = mcp.call(tool_name, tool_input)
        duration_ms = int((time.perf_counter() - start) * 1000)
        prs_in = (raw or {}).get("pull_requests", []) if isinstance(raw, dict) else []

        now = datetime.now(timezone.utc)
        out: list[dict] = []
        for pr in prs_in:
            if pr.get("draft", False):
                continue
            created = datetime.fromisoformat(
                pr["created_at"].replace("Z", "+00:00")
            )
            days_open = (now - created).days
            if days_open < min_age_days:
                continue
            out.append({
                "number":       pr["number"],
                "title":        pr["title"],
                "author":       pr["user"]["login"],
                "days_open":    days_open,
                "review_count": len(pr.get("reviews", [])),
            })

        _audit.log(
            workflow="github_tools",
            tool=tool_name,
            tool_input=tool_input,
            status="success",
            duration_ms=duration_ms,
        )
        return out
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        _audit.log(
            workflow="github_tools",
            tool=tool_name,
            tool_input=tool_input,
            status="error",
            duration_ms=duration_ms,
        )
        print(f"github_tools warning: {exc}", file=sys.stderr)
        return []


def get_priority_issues(
    mcp: "MCPClient",
    repo: str,
    labels: list[str] | None = None,
) -> list[dict]:
    """
    Fetch open issues matching any of the given labels.

    Returns list of dicts: number, title, priority, assignee, days_open.
    Sorted by priority (P0 first, then P1, then others), then days_open desc.
    Returns [] on any error.
    """
    if labels is None:
        labels = ["P0", "P1"]
    tool_name = "github_issues"
    tool_input = {"repo": repo, "state": "open", "labels": labels}
    start = time.perf_counter()
    try:
        raw = mcp.call(tool_name, tool_input)
        duration_ms = int((time.perf_counter() - start) * 1000)
        issues_in = (raw or {}).get("issues", []) if isinstance(raw, dict) else []

        now = datetime.now(timezone.utc)
        out: list[dict] = []
        for issue in issues_in:
            label_names = [
                lbl.get("name", "") for lbl in issue.get("labels", [])
                if isinstance(lbl, dict)
            ]
            if "P0" in label_names:
                priority = "P0"
            elif "P1" in label_names:
                priority = "P1"
            elif label_names:
                priority = label_names[0]
            else:
                priority = "unlabeled"

            assignee_obj = issue.get("assignee")
            assignee = (
                assignee_obj["login"]
                if isinstance(assignee_obj, dict) and assignee_obj.get("login")
                else "unassigned"
            )

            created = datetime.fromisoformat(
                issue["created_at"].replace("Z", "+00:00")
            )
            days_open = (now - created).days

            out.append({
                "number":    issue["number"],
                "title":     issue["title"],
                "priority":  priority,
                "assignee":  assignee,
                "days_open": days_open,
            })

        priority_rank = {"P0": 0, "P1": 1}
        out.sort(key=lambda x: (priority_rank.get(x["priority"], 99), -x["days_open"]))

        _audit.log(
            workflow="github_tools",
            tool=tool_name,
            tool_input=tool_input,
            status="success",
            duration_ms=duration_ms,
        )
        return out
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        _audit.log(
            workflow="github_tools",
            tool=tool_name,
            tool_input=tool_input,
            status="error",
            duration_ms=duration_ms,
        )
        print(f"github_tools warning: {exc}", file=sys.stderr)
        return []


def search_recent_commits(
    mcp: "MCPClient",
    repo: str,
    service: str,
    hours: int = 4,
) -> list[dict]:
    """
    Find commits touching files under services/{service}/ in the last N hours.

    Returns list of dicts: sha_short, author, message, timestamp, files_changed.
    Returns [] on any error.
    """
    tool_name = "github_commits"
    tool_input = {"repo": repo, "path": f"services/{service}/"}
    start = time.perf_counter()
    try:
        raw = mcp.call(tool_name, tool_input)
        duration_ms = int((time.perf_counter() - start) * 1000)
        commits_in = (raw or {}).get("commits", []) if isinstance(raw, dict) else []

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        out: list[dict] = []
        for commit in commits_in:
            timestamp_str = commit["commit"]["author"]["date"]
            ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            if ts < cutoff:
                continue
            author_obj = commit.get("author") or {}
            author = author_obj.get("login", "unknown") if isinstance(author_obj, dict) else "unknown"
            message = commit["commit"]["message"].splitlines()[0]
            out.append({
                "sha_short":     commit["sha"][:7],
                "author":        author,
                "message":       message,
                "timestamp":     timestamp_str,
                "files_changed": len(commit.get("files", [])),
            })

        _audit.log(
            workflow="github_tools",
            tool=tool_name,
            tool_input=tool_input,
            status="success",
            duration_ms=duration_ms,
        )
        return out
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        _audit.log(
            workflow="github_tools",
            tool=tool_name,
            tool_input=tool_input,
            status="error",
            duration_ms=duration_ms,
        )
        print(f"github_tools warning: {exc}", file=sys.stderr)
        return []
