# The Governed AI Pipeline

**Week 3 — AI-Augmented SDLC & Governance**
Status: IN PROGRESS

## Overview

This project builds a complete AI-augmented development pipeline with custom slash commands, governance hooks, audit logging, and measured efficiency metrics. The deliverable is a portable `.claude/` directory that can be dropped into any repository to instantly enable AI-governed development workflows.

The pipeline is designed around Claude Code's extensibility model: slash commands for developer workflows, hooks for safety guardrails, and structured logs for compliance and cost tracking.

## Target Repository

The pipeline operates against the **Week 2 URL shortener** (`week-2/`) as its sample target. When commands need to run against shortener files, copies are placed in `sample-target/` to keep `week-2/` frozen and unmodified. Source files in `sample-target/` are gitignored; only curated demo files are committed.

**Baseline task:** REQ-SHORT-006 (soft delete) is used as the controlled experiment for before/after ROI measurement in Session C.

## 4-Part Structure

### Part 1 — Workflow Mapping & Analysis (15%)
- Mermaid flowchart of the full dev lifecycle (ticket to deploy)
- Automation Leverage Framework with ROI scoring per workflow step
- Top 3 automation targets mapped to the 5 slash commands

### Part 2 — Slash Command Pipeline (25%)
Five custom Claude Code commands in `.claude/commands/`:

| Command | Purpose |
|---------|---------|
| `/review` | AI code review of staged diff against CLAUDE.md conventions |
| `/test-gen` | Generate tests for changed files, run them, report coverage |
| `/commit` | Smart commit message from diff analysis |
| `/ship` | Full pipeline: /review + /test-gen + /commit + gh pr create |
| `/onboard` | Architecture summary + key files + conventions for new hires |

### Part 3 — Governance & Safety (25%)
- **PreToolUse hooks:** Block dangerous bash (`validate-bash.py`), scan for leaked secrets (`check-secrets.py`), enforce file scope (`scope-guard.sh`)
- **PostToolUse hook:** Audit log every tool action to JSONL (`audit-log.sh`)
- **UserPromptSubmit hook:** Log all prompts to JSONL (`prompt-log.sh`)
- **Stop hook:** Generate session summary with cost tracking (`session-summary.sh`)
- **settings.json:** Documented allowlists, denylists, permission mode, cost limits

### Part 4 — Measurement & ROI (20%)
- Baseline: implement REQ-SHORT-006 manually, record time/steps/errors
- With-pipeline: same task using `/ship`, record identical metrics
- ROI report: before/after comparison, weekly savings per dev, annual projection for 10-person team at $150/hr
- Governance controls inventory

## Session Plan

| Session | Focus | Key Deliverables |
|---------|-------|-----------------|
| **A** (kickoff) | Scaffold, Part 1, dashboard | README, CLAUDE.md, workflow-map.md, leverage-analysis.md, index.html |
| **B** (build) | Parts 2 + 3 | 5 slash commands, 6 hooks, settings.json, sample-target setup |
| **C** (measure) | Part 4 | Baseline task, /ship run, roi-report.md, governance-playbook.md |
| **D** (submit) | Report + polish | REPORT.md (12 questions), submission PDF, dashboard COMPLETE |

## Hook Contract Summary

| Variable | Available In | Description |
|----------|-------------|-------------|
| `$CLAUDE_TOOL_NAME` | PreToolUse, PostToolUse | Tool name (Bash, Edit, Write, Read, ...) |
| `$CLAUDE_TOOL_INPUT` | PreToolUse, PostToolUse | JSON string of tool input |
| `$CLAUDE_TOOL_RESULT` | PostToolUse only | Tool execution result |
| `$CLAUDE_FILE_PATH` | Edit, Write | File path being modified |
| `$CLAUDE_USER_PROMPT` | UserPromptSubmit | Raw user prompt text |
| `$CLAUDE_TOKENS` | Stop | Tokens used in session |

**Exit codes:** 0 = allow, 1+ = block (stderr shown to user)
**Matchers:** `"Bash"` `"Edit"` `"Write"` `"Read"` `"Edit|Write"` `"*"` `"Glob"` `"Grep"`

## Repository Structure

```
week-3/
  .claude/
    commands/          # 5 slash commands (review, test-gen, commit, ship, onboard)
    hooks/             # 6 governance hooks (Python + Bash)
    audit/             # Audit logs (JSONL), cost logs, blocked actions, session summaries
    settings.json      # Permission config, hook registration, cost limits
  docs/
    workflow-map.md    # Mermaid flowchart + annotations (Part 1)
    leverage-analysis.md # ROI scoring framework (Part 1)
    roi-report.md      # Before/after measurement (Part 4)
    governance-playbook.md # 6-week team rollout plan (Part 5)
  sample-target/       # Copies of week-2 files for pipeline testing
  CLAUDE.md            # Project-level conventions and workflow rules
  REPORT.md            # Answers to 12 rubric questions
  README.md            # This file
```
