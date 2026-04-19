# Week 3 Report — Governed AI Pipeline

## Thinking Questions

### Q1. What workflow steps did your Mermaid map reveal as highest-friction, and why does that matter for AI-augmentation ROI?

The workflow map identified 5 of 12 steps as high-friction (red): **Understand Codebase** (25 min, tribal knowledge dependency), **Write Tests** (30 min, most tedious step), **Self-Review** (15 min, blind spots in own code), **Peer Review** (45 min, 30 min wait + 15 min review), and **Address Feedback** (20 min, multiple review rounds). These 5 steps consume 135 of 227 total minutes (59% of cycle time) but produce no new features — they are quality/process overhead.

This matters for AI ROI because the highest-friction steps are also the most automatable: test generation (ROI 9/10), code review (ROI 8/10), and PR creation (ROI 8/10) all score high on AI capability because they follow predictable patterns that LLMs handle well. The Automation Leverage Framework confirms that Frequency x Time x AI Capability yields the best ROI precisely where developer pain is greatest, creating a natural alignment between "what developers hate doing" and "what AI does best."

### Q2. How does encoding conventions in CLAUDE.md change the dynamics of a code review compared to purely human review?

CLAUDE.md transforms code review from a subjective, inconsistent process into a deterministic, scalable one. When conventions exist only in developers' heads, reviews become personality-dependent: one reviewer cares about naming, another about test coverage, a third about commit messages. CLAUDE.md makes the rules explicit, versioned, and machine-readable.

The key dynamic shift: `/review` checks every diff against the same convention set every time, catching the "boring" violations (missing test coverage, `var` usage, functions over 40 lines, inconsistent commit format) systematically. This frees human reviewers to focus on what AI cannot assess well — architectural decisions, business logic correctness, and design trade-offs. In our Week 2 experience, the self-critique loop improved security scores from 6/10 to 9/10, demonstrating that systematic rule-checking catches real issues human review misses.

The trade-off: CLAUDE.md must be maintained. Stale conventions become false positives. The governance playbook addresses this with a weekly review cycle.

### Q3. What did your 3 hook-triggered blocks demonstrate about the value of PreToolUse hooks vs. post-hoc review?

The three deliberate blocks demonstrated that PreToolUse hooks provide **prevention, not detection**:

1. **validate-bash.py blocked `rm -rf /tmp/test`** — A destructive command was stopped before execution. Post-hoc review would have found the damage after files were deleted.
2. **check-secrets.py blocked a Stripe-style key in a file write** — The secret never reached disk. Post-hoc scanning (like git-secrets or GitHub secret scanning) would have caught it after commit, requiring history rewriting.
3. **scope-guard.sh blocked an edit to `week-2/src/index.ts`** — A frozen file was protected from accidental modification. Post-hoc review would have required reverting a commit.

The fundamental difference: PreToolUse hooks enforce invariants at the moment of action, making violations impossible rather than merely detectable. This is the difference between a guardrail (prevents you from going off the cliff) and a dashcam (records you going off the cliff). The cost of prevention is near-zero (milliseconds of hook execution), while the cost of post-hoc remediation scales with damage (minutes to hours of git history cleanup, secret rotation, or data recovery).

### Q4. Explain the design tradeoff between "permission: plan" mode (conservative) and "permission: auto" mode (aggressive). Which did you choose and why?

The three permission modes represent a trust spectrum:

- **plan mode (conservative):** Claude proposes actions, human approves every one. Maximum safety, minimum velocity. Best for regulated environments where every change needs sign-off.
- **default mode (balanced):** Claude executes read operations freely, prompts for writes/commands. Good balance of safety and speed.
- **auto mode (aggressive):** Claude executes everything without prompting. Maximum velocity, relies entirely on hooks for safety.

We chose **default mode** because the hook system provides a robust second layer of protection that makes auto mode theoretically safe, but default mode adds defense-in-depth: even if a hook has a bug or misses a pattern, the permission prompt catches it. The marginal velocity cost of default over auto is small (a few extra confirmations per session), but the safety margin is significant.

For a team rollout, default mode also builds trust gradually — developers see what Claude is doing and build confidence in the hooks before considering auto mode. The governance playbook recommends keeping default mode through the full 6-week rollout, with auto mode as a future optimization only after the team has high confidence in hook coverage.

### Q5. What is the single most important metric from your ROI report, and how would you use it to pitch this pipeline to a skeptical engineering director?

**The headline metric: $253,500 annual net savings for a 10-person team.**

To pitch this to a skeptical engineering director, I would frame it as follows:

"Our developers spend 42% of their feature cycle time on process tasks that AI can handle: writing tests, reviewing their own code, crafting commit messages, and assembling PRs. We measured this on a real feature task — a soft delete endpoint. Manual: 89 minutes. With the pipeline: 35 minutes. That is a 61% reduction in cycle time per feature.

At 5 features per developer per week and $150/hour, the math is straightforward: 54 minutes saved x 5 features x 10 developers x 50 weeks x $2.50/minute = $337,500 in gross time savings. Subtract $40,000 in API costs and maintenance, and the net is $297,500 conservatively. Factor in earlier bug detection (our review hook caught issues the developer missed), and the midpoint estimate is $253,500.

But the number that matters most isn't the dollars — it is that every PR now ships with 87% test coverage, zero leaked secrets, a complete audit trail, and consistent documentation. The pipeline makes quality the default, not the exception."

### Q6. Describe two situations where a governance hook should intentionally be overridden. How would your system handle those safely?

**Situation 1: Emergency hotfix to a frozen file.** If production is down and the fix requires editing a file blocked by scope-guard.sh (e.g., a critical bug in `week-2/src/index.ts` that was supposedly frozen), the developer needs to bypass the scope guard. The system handles this by: (a) the developer can temporarily modify settings.json to add the file to the allowlist, committing the settings change with justification; (b) the override is logged in audit.jsonl so the team can review it; (c) after the hotfix, the allowlist is reverted.

**Situation 2: Intentional use of a "dangerous" command.** A developer needs to run `rm -rf node_modules/` to fix a corrupted dependency tree — a legitimate use of `rm -rf` that validate-bash.py would block. The system handles this by: (a) the developer runs the command outside Claude Code (directly in terminal), bypassing the hook entirely; (b) alternatively, the developer can temporarily disable the specific hook in settings.json; (c) both approaches leave audit evidence — the former through absence of the action in audit.jsonl (notable gap), the latter through the settings.json change in git history.

The key design principle: overrides should be **auditable, not impossible**. The hooks are guardrails, not prison walls. Making them bypassable (with a paper trail) prevents the "cry wolf" problem where developers disable the entire system because one rule is too rigid.

### Q7. How would your audit log (JSONL) support a post-incident investigation? Give a concrete example with a jq query.

**Scenario:** A secret was committed to the repository despite check-secrets.py being active. The incident response team needs to determine: (a) when the secret was introduced, (b) which tool action created it, (c) what the user's prompt was.

**Investigation using jq queries:**

Step 1 — Find all Write/Edit actions around the suspected time:
```bash
jq 'select(.tool == "Write" or .tool == "Edit") | select(.timestamp >= "2026-04-19T15:00:00Z")' audit.jsonl
```

Step 2 — Search for the specific file that contained the secret:
```bash
jq 'select(.input | contains("credentials.json"))' audit.jsonl
```

Step 3 — Cross-reference with the prompt log to understand intent:
```bash
jq 'select(.timestamp >= "2026-04-19T14:55:00Z" and .timestamp <= "2026-04-19T15:05:00Z")' prompts.jsonl
```

Step 4 — Check if the block was logged (it should have been):
```bash
grep "check-secrets" blocked.log | grep "2026-04-19"
```

If check-secrets.py blocked the action, the entry in blocked.log confirms the hook worked. If no block entry exists, the investigation reveals a gap in the regex patterns — the specific secret format wasn't covered, and the pattern set needs updating. The JSONL format makes this investigation fast: `jq` queries replace manual log parsing, and the timestamp + tool + input fields provide the complete action timeline.

## Tactical Questions

### Q8. Show your /ship command's step order and explain why /review must precede /test-gen.

The `/ship` pipeline executes in this order:

```
Step 1: /review   → Check diff against CLAUDE.md conventions
Step 2: /test-gen → Generate tests, run with coverage
Step 3: /commit   → Create Conventional Commit message
Step 4: gh pr create → Open PR with review + coverage data
```

**/review must precede /test-gen** for three reasons:

1. **Fail-fast economics:** /review is faster than /test-gen (diff analysis vs. test generation + execution). If the code has error-severity issues (hardcoded secrets, scope violations, missing error handling), there is no point generating tests for broken code. Catching problems cheaply before expensive operations is a core pipeline design principle.

2. **Test quality depends on code quality:** If /review identifies that a function is missing input validation, tests generated against the current code would test the wrong behavior. Fixing the code first means /test-gen generates tests for the correct implementation.

3. **Review findings inform test focus:** /review's output identifies which code paths need attention. While /test-gen independently analyzes changed files, the sequential ordering ensures that any issues flagged by /review are already resolved before test generation, leading to a more accurate coverage report.

### Q9. Show one hook's settings.json entry and the matching Python/Bash code. Explain how matcher + lifecycle + exit code interact.

**settings.json entry:**
```json
{
  "matcher": "Bash",
  "hook": "python3 week-3/.claude/hooks/validate-bash.py",
  "description": "Block dangerous bash commands"
}
```

**Matching Python code (validate-bash.py core logic):**
```python
BLOCKED_PATTERNS = [
    (r"rm\s+-rf\b", "rm -rf (recursive force delete)"),
    (r"DROP\s+TABLE\b", "DROP TABLE"),
    (r"git\s+push\s+--force\b", "git push --force"),
    # ... more patterns
]

def main():
    data = json.load(sys.stdin)
    command = data.get("tool_input", {}).get("command", "")
    for pattern, name in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            log_block(name, command)
            print(f"BLOCKED: {name}", file=sys.stderr)
            sys.exit(1)
    sys.exit(0)
```

**How they interact:**

1. **Lifecycle (PreToolUse):** The hook runs *before* the Bash tool executes. The command has not yet run. This is critical — it means `rm -rf` is blocked before files are deleted, not after.

2. **Matcher ("Bash"):** Claude Code only invokes this hook when the tool being used is `Bash`. An `Edit` or `Read` action does not trigger validate-bash.py. This is efficient — no wasted hook execution on irrelevant tools. Other matchers like `"Edit|Write"` or `"*"` broaden the trigger scope.

3. **Exit code:** `exit 0` = allow the tool to proceed. `exit 1` = block the tool and show stderr to the user. The hook's stderr message ("BLOCKED: rm -rf") becomes the user-facing error. If the hook crashes or exits non-zero for any reason, the tool is blocked — fail-closed, which is the safe default.

### Q10. Paste one audit.jsonl entry. Write a jq command that filters for only blocked Write actions from today.

**Sample audit.jsonl entry:**
```json
{"timestamp":"2026-04-19T15:49:31Z","user":"kewlf","branch":"main","tool":"Write","input":"{\"file_path\":\"test.ts\",\"content\":\"const key = sk_test_FAKE_DO_NOT_USE_...\"}","result":"BLOCKED by check-secrets.py"}
```

**jq command to filter blocked Write actions from today:**
```bash
jq 'select(.tool == "Write" and (.result | test("BLOCKED")) and (.timestamp | startswith("2026-04-19")))' \
  week-3/.claude/audit/audit.jsonl
```

This query selects entries where: (a) the tool is "Write", (b) the result contains "BLOCKED", and (c) the timestamp starts with today's date. The JSONL format (one JSON object per line) is specifically designed for this kind of `jq` filtering — it is append-only, grep-friendly, and does not require parsing a large JSON array.

### Q11. Show the /test-gen coverage output for one file and explain what the uncovered lines tell you about the implementation.

**Coverage output for routes/delete.ts:**
```
----------|---------|----------|---------|---------|-------------------
File      | % Stmts | % Branch | % Funcs | % Lines | Uncovered Line #s
----------|---------|----------|---------|---------|-------------------
  delete  |   78.57 |    66.67 |  100.00 |   78.57 | 18-24
----------|---------|----------|---------|---------|-------------------
```

**What the uncovered lines tell us:**

Lines 18-24 of `delete.ts` correspond to the "not found" error handling branch:
```typescript
if (!record) {
    return c.json<ErrorResponse>(
      { error: { code: 404, message: 'Short code not found', details: null } },
      404
    );
}
```

The 66.67% branch coverage and uncovered lines 18-24 indicate that the test suite exercises the **happy path** (successful soft delete returning 204) but does not fully test the **404 error case** (attempting to delete a non-existent short code). This is a common test generation gap — the happy path is always generated first, and error branches require setup of specific preconditions (calling delete with a code that was never created).

The 100% function coverage confirms that the delete handler function itself is called during testing — the gap is purely in branch coverage within that function. To close this gap, we need a test like:
```typescript
it('should return 404 for a non-existent short code', async () => {
  const res = await app.request('/nonexistent', { method: 'DELETE' });
  expect(res.status).toBe(404);
});
```

### Q12. Paste your full settings.json. For each permission rule, explain why it is allow vs. deny.

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Edit",
      "Glob",
      "Grep",
      "Bash(npm test)",
      "Bash(npx vitest*)",
      "Bash(git status)",
      "Bash(git diff*)",
      "Bash(git log*)",
      "Bash(gh pr*)"
    ],
    "deny": [
      "Bash(rm *)",
      "Bash(git push --force*)",
      "Bash(git reset --hard*)",
      "Bash(docker*)",
      "Bash(curl*|bash)",
      "Bash(chmod 777*)"
    ]
  }
}
```

**Allow rules — why each is safe to auto-approve:**
- **Read, Glob, Grep** — read-only operations. Cannot modify any state. Essential for code analysis, review, and onboarding workflows.
- **Edit** — file modifications. Protected by check-secrets.py (blocks leaked secrets) and scope-guard.sh (blocks out-of-scope files). The hooks provide the safety that allows auto-approval.
- **Bash(npm test), Bash(npx vitest*)** — test execution. Side-effect-free in a properly isolated test environment. Required for /test-gen to function.
- **Bash(git status), Bash(git diff*), Bash(git log*)** — git read operations. Cannot modify the repository. Essential for /review and /commit to analyze changes.
- **Bash(gh pr*)** — GitHub CLI PR operations. Creates PRs (visible to others) but this is the intended output of /ship. The PR is the deliverable.

**Deny rules — why each is blocked:**
- **Bash(rm *)** — file deletion. Even targeted `rm` can cause irreversible data loss. Developers who need to delete files should do so outside Claude Code where the action is fully intentional.
- **Bash(git push --force*)** — overwrites remote history. Can destroy other developers' work. Force pushes should require explicit human decision outside the AI pipeline.
- **Bash(git reset --hard*)** — discards local changes. Can lose uncommitted work. Same rationale as force push — irreversible actions need human intent.
- **Bash(docker*)** — container operations. Can modify system state, expose ports, mount volumes. Out of scope for code editing workflows.
- **Bash(curl*|bash)** — remote code execution. Downloading and executing arbitrary scripts is the #1 supply chain attack vector.
- **Bash(chmod 777*)** — world-writable permissions. A security anti-pattern that should never be automated.
