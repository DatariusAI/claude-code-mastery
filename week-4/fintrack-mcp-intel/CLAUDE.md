# CLAUDE.md — FinTrack MCP Engineering Intelligence Platform

<!-- 
  TASK 5: Complete this file.
  Read the task description in the mini project document before filling this in.
  Another engineer must be able to set up this project using this file alone.
-->

## System Purpose

[TODO: Write a one-paragraph description of what this system does and who it is for.]

## MCP Server Registry

| Server      | URL | Access | Owner |
|-------------|-----|--------|-------|
| github-mcp  |     |        |       |
| pg-mcp      |     |        |       |

## Workflows

### WF-01: Morning Intelligence Brief
- **Trigger:** `python main.py --workflow morning-brief`
- **MCP tools:** [TODO: list the tools called in order]
- **Output:** [TODO: describe the output format]

### WF-02: Incident Triage
- **Trigger:** `python main.py --workflow incident-triage --service <name>`
- **MCP tools:** [TODO: list the tools called in order]
- **Output:** [TODO: describe the JSON schema]

## Architecture Rules

1. All tokens via environment variables only — NEVER hardcode credentials
2. Every MCP tool call must be logged via audit.log()
3. No PII flows through any prompt — use aggregated data only
4. [TODO: Add 2 more rules specific to your implementation]

## Prompt Templates

### morning_brief.txt
[TODO: Paste the prompt you wrote for WF-01]

### incident_triage.txt
[TODO: Paste the prompt you wrote for WF-02]
