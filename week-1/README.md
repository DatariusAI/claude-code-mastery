# Week 1 — Foundations & Claude Code Mental Models

**Status:** COMPLETE

## Mini Project: Codebase Detective (Hono Framework)

AI-assisted deep dive into the [Hono](https://github.com/honojs/hono) web framework source code.

### Artifacts

| Artifact | Location |
|----------|----------|
| AI Onboarding Guide | [`/CLAUDE.md`](../CLAUDE.md) |
| 12-Question Reflections | [`/docs/reflections.md`](../docs/reflections.md) |
| Architecture Diagram | [`/docs/diagrams/architecture.md`](../docs/diagrams/architecture.md) |
| Request Sequence Diagram | [`/docs/diagrams/request-sequence.md`](../docs/diagrams/request-sequence.md) |
| State Diagram | [`/docs/diagrams/state-diagram.md`](../docs/diagrams/state-diagram.md) |
| D3.js Dependency Graph | [`/docs/visualization/dependency-graph.html`](../docs/visualization/dependency-graph.html) |
| Bug Audit | [`/docs/bug-audit.md`](../docs/bug-audit.md) |
| Program Dashboard | [`/index.html`](../index.html) |
| Submission PDF | [`/Mini Project 1 – Codebase Detective – Mohammad Alrashed.pdf`](../) |

### Key Findings

- Hono has **zero production dependencies** — built entirely on Web Standards
- Architecture: `utils → router → core → helpers → middleware → adapters`
- 5 router implementations with SmartRouter auto-selecting the fastest at runtime
- `compose.ts` (73 lines) is the single most critical file to understand
- JSX subsystem is largely self-contained

### Live

- Dashboard: https://datariusai.github.io/claude-code-mastery/
