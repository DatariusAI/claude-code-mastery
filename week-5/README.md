# Week 5 — Multi-Agent Pipelines & Skills

**Status:** IN PROGRESS

## Project overview

A 2-agent code-review pipeline run on a deliberately-flawed Python e-commerce
backend (OrderFlow), then both agent prompts packaged as versioned, parameterised
Skills. Audience: engineering teams who want a reusable agent + Skill library
for code review that survives reuse beyond a single one-off prompt run.

The two agents are run in **separate Claude Code sessions** (per the Analytics
Vidhya brief) so the Architect's framing cannot bias the Security Agent's
findings, and vice versa. Each agent's output is the sole hand-off to the
next stage.

## Layout

| Path | Purpose |
|---|---|
| `orderflow-sample/` | Sanitized Analytics Vidhya scaffold — the agents' target |
| `agent-outputs/` | Frozen outputs of the Architect and Security agents (Sessions A & B) |
| `orderflow-sample/skills/` | Skills library — packaged versions of both agent prompts |
| `docs/` | Pipeline architecture, Skills library reference, self-review, orchestration notes |
| `REPORT.md` | 9-section reflection covering design, fallback, sanitization, security posture |

## Session plan

- **Session A** — scaffold + Architect agent prompt + run + dashboard re-theme
- **Session B** — Security agent prompt + run + fallback exercise (corrupted-input)
- **Session C** — Skills packaging + self-review (100-pt rubric) + REPORT + Mermaid diagrams
- **Session D** — submission PDF + dashboard COMPLETE flip

## Self-review note

Working solo. The brief's peer-review step becomes a self-review against
`orderflow-sample/skills/REVIEW_TEMPLATE.md` (100-point rubric). The
limitations of self-review (calibration bias, no fresh eyes) are
documented explicitly in `REPORT.md` §6 and `docs/self-review.md`.
