# CLAUDE.md

## Repository Purpose

Central portfolio for the Analytics Vidhya "Claude Code Mastery: AI-Augmented Software Engineering" 7-week program. Each week produces a mini project artifact committed here or linked from here.

## Current State

- **Week 1: COMPLETE** — Hono codebase analysis, D3.js dependency graph, 12-question reflections report, GitHub Pages live at https://datariusai.github.io/claude-code-mastery/
- **Week 2: COMPLETE** — Spec-Driven Feature Factory: 4 YAML prompt templates, formal spec (7 FRs, 5 NFRs, 10 scenarios), Hono/TypeScript URL shortener with REQ-ID traceability, 23 vitest tests (100% pass), self-critique loop, traceability matrix, 12-question report
- **Weeks 3–7: UPCOMING**

## How This Repo Is Organized

- `index.html` — 7-week program dashboard (the main deliverable page, served via GitHub Pages)
- `docs/` — Week 1 artifacts: reflections, visualizations, diagrams
- `CLAUDE.md` — AI onboarding guide for Hono framework analysis (Week 1 reference)
- `MINI_PROJECT_SUBMISSION.md` — Submission documentation
- `README.md` — Portfolio overview, no personal info
- `CLAUDE.md` — This file

Future weekly projects may live in separate repos linked from the dashboard and README tracker table.

## When Starting a New Session

1. Run `/init` to reload this context
2. Check which week is IN PROGRESS (see Current State above)
3. Ask the engineer: "Which part of Week N are we working on today?"
4. Read the relevant project files before making any changes
5. Never modify completed weeks without explicit instruction
6. Always run security scan before committing:
   ```bash
   grep -r "sk-ant\|api_key\|password\|personal_email" . --include="*.js" --include="*.ts" --include="*.py" --include="*.env"
   ```

## Git Workflow

- **Branch:** `main` (direct commits for portfolio work)
- **Commit style:** `week-N: [what changed]` or conventional commits (`feat:`, `fix:`, `docs:`)
- Always verify repo visibility before pushing sensitive-adjacent files
- `.env` files are gitignored — never commit them
- Run `gh repo view DatariusAI/claude-code-mastery --json visibility` to confirm public/private status

## Tech Stack Across Projects

- **Week 1:** TypeScript analysis, D3.js visualization, Mermaid diagrams, HTML/CSS
- **Week 2:** Node.js/Hono or FastAPI, YAML specs, Mermaid, Jest/pytest
- **Future:** Python, LangGraph, Docker, GitHub Actions, MCP servers

## Claude Code Behavior Rules for This Project

- **Fidelity matters:** reproduce diagrams and specs exactly, not approximately
- **Security-first:** scan before every commit to public branches
- **No explanatory text mixed into code blocks**
- **Produce complete, runnable outputs** — no partial templates or placeholder stubs
- **When in doubt about week content, ask before editing**
- **Preserve completed work:** Week 1 dashboard content, mermaid diagrams, and D3 graph data must not be modified unless explicitly requested
