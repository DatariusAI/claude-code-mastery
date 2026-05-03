# CLAUDE.md — OrderFlow Sample App

## Project Overview
OrderFlow is a simplified e-commerce backend. This sample repo is used for the
Week 5 Claude Code Mastery mini project on multi-agent pipelines and Skills.

## Module Map
| Module | Purpose | Status |
|---|---|---|
| `payments/processor.py` | Core payment processing, Stripe integration | ⚠️ Has intentional issues |
| `payments/webhook.py` | Stripe webhook handler | ⚠️ Has intentional issues |
| `auth/auth.py` | User login & session management | ⚠️ Has intentional issues |
| `notifications/notifier.py` | Email/SMS notifications | ⚠️ Has intentional issues |
| `tests/` | Existing test suite (sparse) | Needs expansion |
| `skills/` | Your Skill library (you will build this) | Empty — build in lab |

## Coding Standards
- Python 3.10+
- Type hints on all public functions
- Logging via `logging` module (not print statements)
- All secrets via environment variables (no hardcoding)
- SQL via parameterised queries only (no f-string SQL)
- Functions should be ≤ 40 lines; extract helpers if larger

## Out of Scope for This Lab
- Database migrations
- Stripe API integration (all Stripe calls are stubbed)
- Frontend / API layer
- Deployment configuration

## Agent Scope Guidance
When running agents in this project, constrain scope to ONE module at a time.
Recommended starting scope for lab: `payments/processor.py`

Example scope constraint for prompts:
> SCOPE: payments/processor.py only. Do not modify or review other modules.
