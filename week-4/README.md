# Week 4 — MCP Engineering Intelligence Platform

Connecting Claude Code to live business data via the Model Context Protocol (MCP). The deliverable is a real engineering operations tool with audit logging, governed tool calls, and chained multi-step workflows that answer FinTrack's morning-standup and incident-triage questions in under 60 seconds.

The implementation lives in [`fintrack-mcp-intel/`](./fintrack-mcp-intel/) — the Analytics Vidhya starter scaffold extended with two production-style workflows:

- **WF-01 Morning Brief** — chains 3 MCP calls into a 4-section markdown digest for the on-call engineer.
- **WF-02 Incident Triage** — chains 4 MCP calls into a strict JSON triage object with degraded-mode fallback.

**Target audience:** FinTrack engineering operations team — on-call engineers, platform leads, and incident commanders who need fast, audit-traceable answers from chains of MCP calls.

## Session plan

| Session | Scope |
|---|---|
| A | Scaffold drop, `.gitignore` hardening, audit logger (`mcp/audit.py`), W4 dashboard re-theme |
| B | GitHub MCP wrappers (`mcp/github_tools.py`), Morning Brief + Incident Triage workflows + prompts |
| C | `CLAUDE.md`, `ANSWERS.md`, integration tests, `REPORT.md`, governance docs |
| D | Mini Project 4 PDF compilation + dashboard status flip to COMPLETE |

## Status

**IN PROGRESS** — see the Week 4 tab on the dashboard.
