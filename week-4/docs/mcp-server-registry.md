# MCP Server Registry — FinTrack

> Beta header pinned to `mcp-client-2025-04-04` (legacy — see `REPORT.md` Section 5 for migration plan to `mcp-client-2025-11-20`).

| Server      | URL                                | Access Tier                       | Owner                          | Scope                                                                |
|-------------|------------------------------------|-----------------------------------|--------------------------------|----------------------------------------------------------------------|
| github-mcp  | https://api.github.com/mcp/sse     | read-only                         | FinTrack platform team         | `issues:read`, `pull_requests:read`, `contents:read`, `metadata:read`|
| pg-mcp      | https://mcp.postgres.io/sse        | read-only                         | FinTrack data platform team    | role: `readonly` (analytics replica)                                 |
| jira-mcp    | (placeholder, future)              | read-only                         | FinTrack PMO                   | `issues:read`, `sprints:read`                                        |
| slack-mcp   | (placeholder, future)              | write to single channel only      | FinTrack engineering           | post to `#engineering-intel`                                         |

## github-mcp

**Scopes / permissions.** Read-only fine-grained scopes only: Issues (read), Pull Requests (read), Contents (read), Metadata (read). No write scopes ever. The token must be a fine-grained PAT bound to the FinTrack lab repository scope, not a classic PAT with org-wide reach. Justification is in `ANSWERS.md` Q3 — the blast radius of a compromised write-enabled token is unbounded; read-only confines the worst case to information disclosure.

**Auth token flow.** `.env` line `FINTRACK_GITHUB_TOKEN=...` is loaded by `config.py:12` via `python-dotenv`'s `load_dotenv()`, surfaced as `Config.GITHUB_TOKEN`, and consumed only inside `mcp/client.py:_mcp_servers()` where it becomes the `authorization_token` field of the `github-mcp` entry in the `mcp_servers` list passed to the Anthropic SDK. The token never appears in prompts, logs, test fixtures, or version control.

**Data in / out.** In: tool name + tool-input dict (e.g. `github_issues` with `{"repo", "state", "labels"}`). Out: typed dict matching the GitHub REST shape (e.g. `{"issues": [{"number", "title", "labels", "assignee", "created_at", ...}]}`). The wrappers in `mcp/github_tools.py` re-shape the response into the audit-friendly forms documented in their docstrings.

**Security review status.** Approved for read-only at platform-team sign-off. Re-review required if any wrapper begins consuming a new tool name or if scopes change. The `mcp/audit.py` JSONL log is the evidence record.

**Rotation cadence.** Quarterly. PAT lifetime never exceeds 90 days; CI dependency on the token is documented so rotation does not silently break workflows.

## pg-mcp

**Scopes / permissions.** Database role `readonly` on the analytics replica only — never the production write database. Even a SQL-injection vector in a wrapper cannot escalate beyond `SELECT`. The env var `FINTRACK_PG_READ_URL` is named with the `_READ` suffix specifically as a tripwire for code review — see `ANSWERS.md` Q6.

**Auth token flow.** `.env` line `FINTRACK_PG_READ_URL=postgresql://readonly:...@host/db` is loaded by `config.py:13`, surfaced as `Config.PG_READ_URL`, and reaches `mcp/client.py:_mcp_servers()` as the `pg-mcp` entry's `authorization_token`. The connection-string convention keeps username + password + host + db together so they can be rotated atomically.

**Data in / out.** In the lab, `db_tools.py` is a stubbed-out simulator (`get_overnight_alerts`, `get_error_rate`) returning realistic-looking dicts; in production, those wrappers would issue typed MCP calls to the pg-mcp server. The simulated shapes are intentionally identical to what production would return so workflow code does not change.

**Security review status.** Approved for read-only on the analytics replica. Any tool wrapper that wants to issue a non-`SELECT` statement must trigger Architecture Rule 4: separate registry entry, manager sign-off, elevated audit retention. As of this PR, no such wrapper exists.

**Rotation cadence.** 30 days for the database password (managed by data-platform team); 90 days for the connection string itself.

## jira-mcp (placeholder)

**Scopes / permissions.** When activated, scopes will be `issues:read`, `sprints:read`. No write scopes (PMO does not need this workflow to *create* tickets, only to read them).

**Auth token flow.** `.env` lines `FINTRACK_JIRA_TOKEN=...` and `FINTRACK_JIRA_BASE_URL=...` already exist in `.env.example` for forward compatibility but are not read by any wrapper today. When activated, they will reach `mcp/client.py` via the same `Config` pattern used for github-mcp and pg-mcp.

**Data in / out.** Reserved for a future Sprint Health workflow that aggregates burndown, blocker count, and at-risk-tickets per sprint.

**Security review status.** Not yet reviewed — registry entry is placeholder only. Activation requires the same review process as github-mcp.

**Rotation cadence.** Quarterly (matching github-mcp's PAT cadence).

## slack-mcp (placeholder)

**Scopes / permissions.** This is the only entry on the registry that contemplates a *write* tier — limited to posting messages into a single channel (`#engineering-intel`). No read scopes, no message editing, no DM access. Per Architecture Rule 4, activation requires manager sign-off and elevated audit retention.

**Auth token flow.** `.env` line `FINTRACK_SLACK_WEBHOOK=https://hooks.slack.com/services/...` is reserved. Webhook URLs are themselves the credential — they cannot be granted additional scopes by the receiver, which is the whole reason this is the simplest write tier to safely operate.

**Data in / out.** Reserved for a "post the morning brief to Slack" follow-up workflow. Posts only — never reads channel history.

**Security review status.** Not yet reviewed. Activation will require: separate registry entry beyond this placeholder, manager sign-off (Architecture Rule 4), audit retention bumped from default to 1 year, and a rotation cadence of 30 days on the webhook URL because revocation is the only meaningful security boundary.

**Rotation cadence.** 30 days when activated.
