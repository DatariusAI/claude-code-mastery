# ANSWERS.md — FinTrack MCP Engineering Intelligence Platform

## Q1 — MCP tool call vs regular API call

A regular API call is imperative: the developer hardcodes the endpoint, method, headers, and payload, and the program decides which call to make. An MCP tool call is declarative: each MCP server publishes a typed tool description, and Claude (the model) chooses *which* tool to call and *with what input* based on the prompt and the available schemas (see `mcp/client.py:36-53` for how `_mcp_servers()` registers github-mcp and pg-mcp). This matters for governance because a single audit logger (`mcp/audit.py:45`) can wrap *every* call regardless of which tool fires, and the central server registry (CLAUDE.md Section 2) becomes the one place to enforce credentials, scopes, and approval. It also makes workflows composable: WF-02 chains four heterogeneous calls without the workflow code knowing the wire protocol of either provider.

## Q2 — Sketch JSON for an MCP tool call fetching open issues labelled P0

Using the shape consumed by `MCPClient.call()` in `mcp/client.py:55-105`:

```json
{
  "type": "url",
  "url": "https://api.github.com/mcp/sse",
  "name": "github-mcp",
  "tool_call": {
    "name": "github_issues",
    "input": {
      "repo": "owner/repo",
      "state": "open",
      "labels": ["P0"]
    }
  }
}
```

The wrapper that produces this is `mcp/github_tools.py::get_priority_issues` — it builds the `tool_input` dict, hands it to `mcp.call("github_issues", tool_input)`, and after the call records the audit entry with `_audit.log(workflow="github_tools", tool="github_issues", tool_input=..., status="success", duration_ms=...)`.

## Q3 — Why must the GitHub PAT be read-only?

If a write-enabled token is compromised — for example via a prompt-injection payload that makes it through `prompts/morning_brief.txt` or `prompts/incident_triage.txt` — an attacker could chain it through MCP to *create* issues, *delete* branches, or *modify* code in the lab repo and any other repo the token owner can write to. With a read-only token (scopes `issues:read`, `pull_requests:read`, `contents:read`, `metadata:read`, per CLAUDE.md Section 2), the worst case collapses to information disclosure: the attacker may read what the token can already read, but cannot mutate. This is the principle of least privilege: grant exactly the permissions a task needs, no more. Architecture Rule 4 in `CLAUDE.md` makes read-only the default tier and forces a separate registry entry, manager sign-off, and elevated audit retention before any write tier is added.

## Q4 — BaseWorkflow.run() pattern

`workflows/base.py:36-52` wraps every workflow execution with: a start-time `time.perf_counter()`, a `try`/`except` around `self.execute(**kwargs)`, an end-time elapsed-millisecond log on the success path, an elapsed log + `traceback.print_exc()` + re-raise on the exception path, and rich-styled console output for both. This matters for governance because it gives every workflow the same observability surface — a consistent timing instrument and a consistent exception handler — so adding a new workflow does not require re-implementing logging policy. The audit logger (`mcp/audit.py`) sits one layer below at the per-tool-call boundary, while `run()` provides the per-workflow boundary; together they produce a hierarchical record of which workflow ran and which tools it triggered.

## Q5 — AuditLogger fields and input_hash

The six required fields are `timestamp` (ISO 8601 UTC with `Z` suffix), `workflow` (e.g. `morning_brief`), `tool` (e.g. `github_issues`), `input_hash` (SHA-256 hex of the JSON-sorted input), `status` (`success` or `error`), and `duration_ms` (integer milliseconds). The hash replaces the raw input for three reasons: **privacy** — raw inputs may contain repository owners, label names, or service identifiers we do not want to ship to a downstream log shipper; **storage cost** — a 64-character hex digest is constant size regardless of the call, while raw inputs grow without bound; **tamper detection** — re-hashing a stored entry's claimed input and comparing against the persisted `input_hash` confirms the entry has not been silently rewritten. `tests/test_audit.py:39-47` enforces the privacy property by asserting that a `ghp_secret123` test value never appears in the on-disk log.

## Q6 — FINTRACK_PG_READ_URL

The `_READ` suffix on the env var name is a convention, not a kernel-level enforcement: `config.py:13` only loads the string. The enforcement happens at the database role level — the PG MCP server is configured with the `readonly` role on the analytics replica (see CLAUDE.md Section 2), so even a SQL-injection vulnerability in a tool wrapper cannot escalate beyond `SELECT`. The naming is a tripwire for reviewers: any code that needs write access must add a *separate* env var (e.g. `FINTRACK_PG_WRITE_URL`), which forces the reviewer to notice the new credential, opt in inside `config.py`, and apply the elevated audit-retention rule from Architecture Rule 4. One env var per privilege tier means least-privilege is the default and write access is an explicit, reviewable change.

## Q7 — Why two DB queries in WF-02?

The first call (`db_tools.get_error_rate(service, window_minutes=30)`) establishes the recent baseline — what does this service's error rate look like over the last half hour? The second call (`window_minutes=5`) takes the current snapshot — what is the rate right now? Comparing the two is what detects a *spike*: the prompt's escalation rule fires when `error_rate_now > 3 * error_rate_30min_avg`. Between the two calls, the workflow also fetches `search_recent_commits` and `get_priority_issues`, so by the time Claude evaluates the second number it has the recent-deploy list and the open-bug list as context. This is why the order in `incident_triage.py` is 30-min then commits then bugs then 5-min: the second DB read is most relevant and the model reasons over it with all surrounding context already in the prompt.

## Q8 — Graceful degradation pseudocode

```text
try:
    data_prs = get_open_prs(mcp, repo)
except Exception as exc:
    print(exc, file=stderr)
    data_prs = []
    degraded["github"] = True

try:
    data_issues = get_priority_issues(mcp, repo)
except Exception as exc:
    print(exc, file=stderr)
    data_issues = []
    degraded["github"] = True

data_alerts = get_overnight_alerts()  # local stub — assumed reliable

if degraded["github"]:
    partial_brief = build_brief_with_only_alerts(data_alerts)
    partial_brief += "\n[DEGRADED] GitHub MCP unavailable; PR/issue sections empty"
    return partial_brief
else:
    return full_brief(data_prs, data_issues, data_alerts)
```

In `workflows/incident_triage.py` this pattern is realised concretely: each of the four data fetches has its own `try/except`; on failure we log to stderr, substitute an empty default (`{}` or `[]`), and continue. After the chained calls, the workflow runs `mcp.ask()`, strips fences, parses JSON, and validates the seven required keys; any failure of those final steps returns `ESCALATE_FALLBACK` with `service` set and `escalate=True`. This satisfies Architecture Rule 5: workflows must return a valid output structure even when individual tool calls fail.
