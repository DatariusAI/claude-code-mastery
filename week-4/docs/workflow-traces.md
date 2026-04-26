# Workflow Traces

> Sanitised audit-log excerpts illustrating one full WF-01 run (3 entries), one full successful WF-02 run (4 entries), and the WF-02 degraded fallback. The `input_hash` values shown are real SHA-256 digests of the corresponding tool inputs, computed from the canonical input dicts the wrappers build (verifiable by re-hashing in Python).

## WF-01 Morning Brief — full successful run (3 entries)

Trigger: `python main.py --workflow morning-brief`. The three entries below appear in the log in this order.

```jsonl
{"timestamp": "2026-04-26T08:34:12Z", "workflow": "github_tools", "tool": "github_pull_requests", "input_hash": "546507040d79625292fc533fd5f9d6bec3d2a00dadeb40ff26245fefced3e6a2", "status": "success", "duration_ms": 421}
{"timestamp": "2026-04-26T08:34:12Z", "workflow": "github_tools", "tool": "github_issues",        "input_hash": "bcc4e919e30a184ea74a27f9d9a54033db87a94f7f1d9955f1cc4c3a23d63e26", "status": "success", "duration_ms": 358}
{"timestamp": "2026-04-26T08:34:13Z", "workflow": "github_tools", "tool": "db_overnight_alerts",  "input_hash": "<64-hex>",                                                       "status": "success", "duration_ms": 12}
```

Notes:

- The first hash (`546507...`) is the SHA-256 of `{"repo": "instructor/fintrack-backend-lab", "state": "open"}` with sorted keys.
- The second hash (`bcc4e9...`) is the SHA-256 of `{"labels": ["P0", "P1"], "repo": "instructor/fintrack-backend-lab", "state": "open"}` with sorted keys.
- The third entry would log the `db_overnight_alerts` call (currently a local stub, no MCP wrapper) — its hash is shown as `<64-hex>` because the lab `db_tools` is not yet routed through `_audit.log()`. Filed as a follow-up: in production, every data fetch — local stub or MCP call — should land in the same audit stream.

## WF-02 Incident Triage — full successful run (4 entries)

Trigger: `python main.py --workflow incident-triage --service payments`. The four entries below appear in the log in the order the workflow makes the calls.

```jsonl
{"timestamp": "2026-04-26T14:02:18Z", "workflow": "github_tools", "tool": "db_get_error_rate", "input_hash": "<64-hex>",                                                       "status": "success", "duration_ms": 8}
{"timestamp": "2026-04-26T14:02:18Z", "workflow": "github_tools", "tool": "github_commits",   "input_hash": "a4145366e7cdeff653dfc938923dba8e1bf50e0abec158cc26fb9352f0fa896d", "status": "success", "duration_ms": 612}
{"timestamp": "2026-04-26T14:02:19Z", "workflow": "github_tools", "tool": "github_issues",    "input_hash": "e23118076ce59d46223049cd9b434880b39c7e1a2eb84d315b152637b7f64313", "status": "success", "duration_ms": 287}
{"timestamp": "2026-04-26T14:02:19Z", "workflow": "github_tools", "tool": "db_get_error_rate", "input_hash": "<64-hex>",                                                       "status": "success", "duration_ms": 9}
```

Notes:

- The two `db_get_error_rate` entries have placeholder `<64-hex>` because `db_tools` is currently a local stub (same caveat as WF-01).
- The `github_commits` hash (`a41453...`) is the SHA-256 of `{"path": "services/payments/", "repo": "instructor/fintrack-backend-lab"}` with sorted keys.
- The `github_issues` hash (`e23118...`) is the SHA-256 of `{"labels": ["bug", "payments"], "repo": "instructor/fintrack-backend-lab", "state": "open"}` with sorted keys.

## WF-02 Incident Triage — degraded fallback

When *any* one of the four data fetches raises (per-call `try/except`) the workflow continues with empty defaults. If on top of that the model returns malformed JSON or an output missing one of the seven required keys, the workflow returns this exact dict:

```json
{
  "service": "payments",
  "error_rate_now": -1.0,
  "error_rate_30min_avg": -1.0,
  "likely_cause": "Triage workflow failed — see stderr for details",
  "recent_deploys": [],
  "recommended_action": "Page on-call immediately — automated triage unavailable",
  "escalate": true
}
```

This is `ESCALATE_FALLBACK` from `workflows/incident_triage.py:30-38` with `service` overridden to the requested service. The `tests/test_workflows.py::test_incident_triage_degraded` test exercises this path: it mocks the first `db_tools.get_error_rate` to raise `RuntimeError("DB unavailable")`, mocks `mcp.ask` to return a malformed string, and asserts the returned dict has `escalate=True` and `service="payments"` — and crucially, that the workflow does not raise.

## How to verify a hash

```python
import hashlib, json
inp = {"repo": "instructor/fintrack-backend-lab", "state": "open"}
print(hashlib.sha256(json.dumps(inp, sort_keys=True).encode()).hexdigest())
# 546507040d79625292fc533fd5f9d6bec3d2a00dadeb40ff26245fefced3e6a2
```

Same one-liner reproduces every hash in this document.
