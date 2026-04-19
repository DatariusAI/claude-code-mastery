# Audit Data Flow

```mermaid
flowchart LR
    subgraph inputs["Claude Code Session"]
        A1["Tool Actions\n(Bash, Edit, Write,\nRead, Glob, Grep)"]
        A2["User Prompts"]
        A3["Session End"]
        A4["Blocked Actions\n(hook exit 1)"]
    end

    subgraph hooks["Hook Layer"]
        H1["audit-log.sh\n(PostToolUse)"]
        H2["prompt-log.sh\n(UserPromptSubmit)"]
        H3["session-summary.sh\n(Stop)"]
        H4["validate-bash.py\ncheck-secrets.py\nscope-guard.sh\n(PreToolUse)"]
    end

    subgraph storage["JSONL Storage\n(.claude/audit/)"]
        S1["audit.jsonl\ntimestamp, user, branch,\ntool, input, result"]
        S2["prompts.jsonl\ntimestamp, prompt"]
        S3["costs.jsonl\ntimestamp, tokens,\nestimated_cost_usd"]
        S4["blocked.log\ntimestamp, hook,\ntarget, reason"]
        S5["session-summary.md\nfiles, blocks, tokens, cost"]
    end

    subgraph queries["Compliance Queries"]
        Q1["jq 'select(.tool==\"Write\"\nand (.result|test(\"BLOCKED\")))'\naudit.jsonl"]
        Q2["jq 'select(.timestamp >=\n\"2026-04-19\")'\nprompts.jsonl"]
        Q3["jq '[.tokens] | add'\ncosts.jsonl"]
        Q4["grep -c BLOCKED\nblocked.log"]
    end

    A1 --> H1 --> S1
    A2 --> H2 --> S2
    A3 --> H3 --> S3
    A3 --> H3 --> S5
    A4 --> H4 --> S4

    S1 --> Q1
    S2 --> Q2
    S3 --> Q3
    S4 --> Q4

    Q1 --> R["📊 Compliance\nReport"]
    Q2 --> R
    Q3 --> R
    Q4 --> R

    style A1 fill:#58a6ff,color:#fff,stroke:#1f6feb
    style A2 fill:#bc8cff,color:#fff,stroke:#8b5cf6
    style A3 fill:#f778ba,color:#fff,stroke:#db61a2
    style A4 fill:#da3633,color:#fff,stroke:#b62324
    style S1 fill:#161b22,color:#e6edf3,stroke:#30363d
    style S2 fill:#161b22,color:#e6edf3,stroke:#30363d
    style S3 fill:#161b22,color:#e6edf3,stroke:#30363d
    style S4 fill:#161b22,color:#e6edf3,stroke:#30363d
    style S5 fill:#161b22,color:#e6edf3,stroke:#30363d
    style R fill:#3fb950,color:#fff,stroke:#238636
```

## Log Formats

### audit.jsonl (one entry per tool action)
```json
{"timestamp":"2026-04-19T15:49:40Z","user":"kewlf","branch":"main","tool":"Bash","input":"{\"command\":\"git status\"}","result":"On branch main"}
```

### prompts.jsonl (one entry per user prompt)
```json
{"timestamp":"2026-04-19T15:45:00Z","prompt":"Run /review on the staged diff"}
```

### costs.jsonl (one entry per session)
```json
{"timestamp":"2026-04-19T15:00:00Z","tokens":28400,"estimated_cost_usd":"0.2272","branch":"main"}
```

### blocked.log (one line per blocked action)
```
[2026-04-19T15:49:28Z] BLOCKED validate-bash.py "rm -rf /tmp/test" reason="rm -rf (recursive force delete)"
```

## Example Investigation

**Scenario:** Find all blocked secret leaks in the past week.

```bash
# Count blocks by hook
grep "BLOCKED" .claude/audit/blocked.log | awk '{print $3}' | sort | uniq -c

# Find the prompts that led to blocked actions (within 1 min)
jq 'select(.timestamp >= "2026-04-19T15:49:00Z" and .timestamp <= "2026-04-19T15:50:00Z")' \
  .claude/audit/prompts.jsonl

# Total tokens spent this session
jq '[.tokens] | add' .claude/audit/costs.jsonl
```
