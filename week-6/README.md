# Week 6 — Ship It: CI/CD & Docker for HealthTrack

> Status: **IN PROGRESS** · Last modified: 2026-05-10

A complete CI/CD pipeline and container stack for the HealthTrack
patient-vitals API. This week is **operational**, not feature work
— the HealthTrack source ships with intentional security bugs that
stay in place so the AI-Skill CI gate has something to fire on.
The deliverable is the pipeline that catches them and the runtime
that ships the app.

## What lands here

- A 4-job GitHub Actions pipeline (`lint → test+coverage → security`,
  `→ ai-skills` blocking on CRITICAL findings)
- A multi-stage production Dockerfile (builder + slim runtime,
  non-root, HEALTHCHECK)
- A 3-service docker-compose stack (api + postgres + redis,
  health-gated startup)
- A customised PR template (Performance / Migrations / Feature flags)
- An end-to-end test that proves a `git push` runs the full pipeline

## Layout

| Path | Contents |
|---|---|
| [`healthtrack-api/`](./healthtrack-api/) | The app + scaffolded Skills + `.github/workflows/ci.yml` + (later) Dockerfile + docker-compose.yml |
| [`docs/`](./docs/) | Architecture diagrams (CI pipeline, Docker, end-to-end flow) and reflection notes |
| [`evidence/`](./evidence/) | CI green screenshot, `docker compose ps`, `validate_ci.py` outputs, push-protection unblock URL, final PR link |

## Sessions

| Session | Focus | Lands |
|---|---|---|
| **A** | CI Pipeline + scaffold | `ci.yml`, PR template, dashboard re-theme, scaffold dropped, teaching-fixture decisions documented |
| **B** | Dockerfile | Multi-stage Dockerfile, `.dockerignore`, `/health` endpoint, `validate_ci_part2.txt` |
| **C** | docker-compose + REPORT | 3-service stack, `.env.example`, `.env`, mermaid diagrams, REPORT.md, `validate_ci_part3.txt` |
| **D** | End-to-end test + submission | Real PR triggers full pipeline, evidence collected, MP6 submission PDF, dashboard checklist ticked |

## Grading rubric (100 + 10 bonus)

| # | Item | Points |
|---:|---|---:|
| 1 | CI workflow exists at `.github/workflows/ci.yml` and triggers on PR + push to main | 15 |
| 2 | Pipeline has lint, test (with ≥80% coverage gate), security, and ai-skills jobs with correct `needs:` ordering | 25 |
| 3 | Multi-stage production Dockerfile (builder + slim runtime, non-root, HEALTHCHECK, `EXPOSE`, Python env vars) | 20 |
| 4 | `docker-compose.yml` with api + postgres + redis, health-checked, named volumes, `depends_on: condition: service_healthy` | 15 |
| 5 | `.env.example` committed; real `.env` gitignored; no real secrets reachable from `git log` | 10 |
| 6 | `/health` endpoint reports DB + cache sub-checks; container `HEALTHCHECK` exits non-zero on failure | 10 |
| 7 | `REPORT.md` answers all reflection questions with concrete evidence | 5 |
| **Bonus** | Customised PR template (Performance, Migrations, Feature Flags) + AI-Skill review summary in PR comments | **+10** |

## House rules

- Do not modify `scripts/validate_ci.py` — it is the rubric oracle
- The 4 hardcoded "secrets" in `app/auth.py`, `app/vitals.py`,
  `app/alerts.py`, `app/__init__.py` are **teaching fixtures**.
  See [`healthtrack-api/SECURITY_FIXTURES.md`](./healthtrack-api/SECURITY_FIXTURES.md)
- Never push directly to main; every change goes through a feature
  branch and a PR
- Pre-push security scan from repo root before every push (see
  root `CLAUDE.md`)
