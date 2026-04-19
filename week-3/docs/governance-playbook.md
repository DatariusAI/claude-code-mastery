# Governance Playbook — 6-Week Team Rollout

## Overview

This playbook describes how to roll out the Governed AI Pipeline to a development team over 6 weeks. The approach is incremental: start with low-risk, high-value tools (slash commands), then layer in governance hooks, then enforce compliance policies. Each week builds on the previous one, with clear success criteria before advancing.

## Prerequisites

- Claude Code CLI installed for all team members
- Repository has a CLAUDE.md with team conventions
- Team lead has reviewed settings.json configuration
- Audit log storage location agreed upon (default: `.claude/audit/`)

## Week-by-Week Rollout

### Week 1: Introduction & /onboard + /commit

**Goal:** Get every developer using Claude Code with zero friction. Start with the two least-disruptive commands.

**Actions:**
- Install Claude Code CLI for all team members
- Deploy `/onboard` command — run it once, share output as team wiki page
- Deploy `/commit` command — developers opt-in to using it for commit messages
- Set permission mode to `default` (prompts for dangerous ops, allows reads freely)
- No hooks enabled yet

**Success criteria:**
- 100% of team has Claude Code installed
- 80%+ of commits use `/commit` by end of week
- Zero incidents or pushback

**Risk:** Low — commands are opt-in, no enforcement

---

### Week 2: /review + /test-gen

**Goal:** Add AI code review and test generation. Still opt-in.

**Actions:**
- Deploy `/review` command — developers run before opening PRs
- Deploy `/test-gen` command — developers use for test scaffolding
- Share CLAUDE.md conventions — team reviews and agrees on standards
- Collect metrics: time-per-PR before vs after /review adoption

**Success criteria:**
- 70%+ of PRs have /review run before submission
- Test coverage increases by 5+ points on average
- Developers report time savings in weekly retro

**Risk:** Low-medium — /review may flag issues developers disagree with. Address by tuning CLAUDE.md rules based on feedback.

---

### Week 3: /ship Pipeline + Audit Logging

**Goal:** Chain the full pipeline and start logging for visibility.

**Actions:**
- Deploy `/ship` command — chains /review + /test-gen + /commit + PR create
- Enable `audit-log.sh` (PostToolUse) — log all tool actions to JSONL
- Enable `prompt-log.sh` (UserPromptSubmit) — log prompts for review
- Enable `session-summary.sh` (Stop) — auto-generate session reports
- Share audit dashboard or jq queries for team visibility

**Success criteria:**
- 50%+ of PRs created via /ship
- Audit logs accumulating without issues
- Team comfortable with logging (transparent, not surveillance)

**Risk:** Medium — some developers may resist logging. Mitigate by being transparent about what's logged and why, and by making logs useful (not punitive).

---

### Week 4: PreToolUse Hooks (Validation)

**Goal:** Enforce safety guardrails. This is the first week with blocking hooks.

**Actions:**
- Enable `validate-bash.py` — block dangerous bash commands
- Enable `check-secrets.py` — block secret leaks in edits
- Enable `scope-guard.sh` — enforce file scope boundaries
- Run deliberate trigger tests to demonstrate hooks work (rm -rf, fake key, out-of-scope edit)
- Publish blocked.log review process — weekly review by team lead

**Success criteria:**
- All 3 hooks active with zero false positives in first week
- At least 1 genuine block logged (accidental rm -rf or scope violation)
- Team understands how to request scope exceptions

**Risk:** Medium-high — false positives will cause frustration. Mitigate by starting with conservative blocklists and adding patterns gradually. Have a clear escalation path for false positives.

---

### Week 5: settings.json Hardening + Cost Controls

**Goal:** Lock down permissions and add budget controls.

**Actions:**
- Configure `permissions.allow` and `permissions.deny` in settings.json
- Set `--max-budget-usd` per session ($5 normal, $15 for /ship)
- Set `--max-turns` limits (50 normal, 100 for /ship)
- Enable cost tracking in `costs.jsonl`
- Review first month of audit data — identify patterns, tune rules

**Success criteria:**
- Zero unauthorized command executions
- Cost per developer under $50/week
- Audit data reviewed in team retrospective

**Risk:** Low — by this point team is comfortable with the tools. Cost controls may need tuning based on actual usage patterns.

---

### Week 6: Full Enforcement + Compliance Review

**Goal:** Pipeline is mandatory for all PRs. Compliance audit using accumulated data.

**Actions:**
- Make /ship mandatory for all PRs (enforced via PR template or CI check)
- Conduct first compliance audit using audit.jsonl and blocked.log
- Generate ROI report from real data (time savings, coverage improvements, blocks)
- Document exceptions process for edge cases
- Present results to engineering leadership

**Success criteria:**
- 100% of PRs go through /ship pipeline
- Compliance audit passes with documented evidence
- ROI report shows positive return (target: >$200/dev/week saved)
- Leadership approves continued use and budget

**Risk:** Low — 5 weeks of gradual adoption means the team is already habituated. Main risk is edge cases that require manual override.

---

## Rollback Plan

If any week introduces unacceptable friction:

1. **Disable the problematic hook/command** — each hook can be individually removed from settings.json
2. **Keep logging active** — audit-log.sh and prompt-log.sh have zero user impact
3. **Revert to previous week's configuration** — settings.json is version-controlled
4. **Post-mortem** — analyze what went wrong, adjust the pattern/threshold, re-deploy next sprint

## Compliance Mapping

| Compliance Requirement | Pipeline Control | Evidence Source |
|----------------------|-----------------|----------------|
| **No secrets in source code** | check-secrets.py (PreToolUse) | blocked.log entries with "Potential [type] detected" |
| **No unauthorized file modifications** | scope-guard.sh (PreToolUse) | blocked.log entries with "frozen completed week" |
| **No destructive commands** | validate-bash.py (PreToolUse) | blocked.log entries with "rm -rf", "DROP TABLE", etc. |
| **Complete audit trail** | audit-log.sh (PostToolUse) | audit.jsonl — every tool action with timestamp, user, branch |
| **Prompt accountability** | prompt-log.sh (UserPromptSubmit) | prompts.jsonl — every user prompt logged |
| **Session cost tracking** | session-summary.sh (Stop) | costs.jsonl — tokens, estimated cost per session |
| **Code review before merge** | /review via /ship pipeline | ship-sample-run.md — review findings in PR body |
| **Test coverage minimum** | /test-gen via /ship pipeline | test-gen-sample-output.txt — 80%+ coverage enforced |
| **Consistent commit messages** | /commit via /ship pipeline | git log — Conventional Commits format |
| **Permission least-privilege** | settings.json allow/deny lists | settings.json — documented rationale per rule |

## Metrics to Track

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time per feature | <50 min (from 89 min baseline) | Developer self-report + session-summary.sh |
| Test coverage | >80% on all PRs | /test-gen output in audit/ |
| Blocks per week | <5 (indicates good habits forming) | blocked.log line count |
| False positive rate | <2% of blocks | Manual review of blocked.log |
| Cost per developer per week | <$50 | costs.jsonl aggregation |
| /ship adoption rate | 100% by Week 6 | PR metadata (Generated by /ship) |
| Developer satisfaction | >7/10 | Anonymous survey at Weeks 3 and 6 |
