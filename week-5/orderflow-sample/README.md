# OrderFlow — Sample App for Week 5 Mini Project

**Claude Code Mastery — Week 5: Multi-Agent Pipelines & Skills**

---

## What Is This?

This is a simplified Python e-commerce backend with **intentional flaws** built in.
You will use it as the target for your multi-agent review pipeline and Skill library.

## Setup

No external dependencies needed for the lab. All Stripe and DB calls are stubbed.

```bash
# Optional: run existing tests to see baseline coverage
pip install pytest
pytest tests/ -v
```

## Module Overview

```
payments/
  processor.py   ← START HERE — your agent will review this
  webhook.py     ← Secondary target (stretch goal)
auth/
  auth.py        ← Authentication module (stretch goal)
notifications/
  notifier.py    ← Notifications (stretch goal)
tests/
  test_processor.py  ← Sparse tests — the Test Agent will expand these
skills/
  README.md          ← Your Skill library (you build this in Part 2)
  SKILL_TEMPLATE.md  ← Template for your SKILL.md files
  REVIEW_TEMPLATE.md ← Peer review checklist
CLAUDE.md        ← Project context — always pass this to your agents
```

## Recommended Starting Scope

For Part 1, focus your agents on **`payments/processor.py` only**.

It has:
- Missing input validation
- A hardcoded API key (security issue)
- SQL injection risk
- Unsafe PII exposure
- Sparse test coverage

These are deliberate — they give your agents real findings to work with.

## Stretch Goals

Once you've completed all 3 parts with `processor.py`:
- Re-run your pipeline on `auth/auth.py`
- Add a third Skill (e.g. a Complexity Audit Skill)
- Chain your two Skills in a GitHub Actions YAML (see Session 10 slides)
