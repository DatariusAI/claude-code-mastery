# CLAUDE.md — Week 3 Project Conventions

This file encodes the team's development standards for the Governed AI Pipeline project.
All Claude Code slash commands (especially `/review`) check code against these rules.

## Commit Format

- Format: `week-3: <short description>` (lowercase, imperative mood)
- Max subject line: 72 characters
- Body: optional, separated by blank line, wraps at 80 characters
- Reference issue numbers where applicable: `fixes #123`
- Examples:
  - `week-3: add validate-bash hook for dangerous command blocking`
  - `week-3: fix scope-guard to allow sample-target edits`

## Branch Conventions

- Primary branch: `main` (direct commits for portfolio work)
- Feature branches: `week-3/<feature>` when using `/ship` for PR creation
- Branch names: lowercase, hyphen-separated, prefixed with `week-3/`

## PR Template

PRs created by `/ship` must include:
- **Summary:** 1-3 bullet points describing changes
- **Test plan:** how changes were verified (test output, manual steps)
- **Governance:** which hooks were active, any blocks encountered
- One logical change per PR

## Architecture (Target: Week 2 URL Shortener)

- **Runtime:** Node.js with Hono framework on TypeScript
- **Module system:** ESM (`import`/`export`)
- **Structure:**
  - `src/index.ts` — App entry point
  - `src/routes/` — Route handlers (shorten, redirect, delete, analytics)
  - `src/lib/` — Business logic (store, validator, shortener)
  - `tests/` — Vitest test files
- **Environment:** Config via `.env` file (gitignored)

## Testing Standards

- **Framework:** Vitest
- **Minimum coverage threshold:** 80% line coverage
- **Test file naming:** `<module>.test.ts` in `tests/` directory
- **Required test types:**
  - Unit tests for all business logic modules
  - Integration tests for all API endpoints
  - Edge cases: empty input, invalid input, boundary values, expiration
- **Mocking:** Mock external dependencies only; use real in-memory store
- **Each test must be independent:** no shared mutable state between tests
- **What /test-gen should generate:**
  - Tests for every exported function in changed files
  - Happy path + at least 2 error/edge cases per function
  - Coverage report output appended to test-gen-sample-output.txt

## File Scope Rules

These rules are enforced by `scope-guard.sh`. Edits outside allowed paths are blocked.

**Allowed paths for edits:**
- `week-3/` — all project files
- `index.html` — dashboard updates (root file)

**Blocked paths:**
- `week-1/` — frozen, completed
- `week-2/` — frozen, completed (use sample-target/ copies instead)
- `docs/` (root) — Week 1 visualization assets, frozen
- `CLAUDE.md` (root) — repo-wide conventions, frozen
- `README.md` (root) — portfolio overview, frozen
- `.env` — never tracked

## Security Rules

- Never hardcode API keys, passwords, or tokens in source files
- All secrets must come from environment variables
- Never commit `.env` files (enforced by .gitignore)
- No `sk-ant-` strings in any tracked file
- No personal email addresses in tracked files
- No absolute paths (`/Users/`, `C:\Users\`) in tracked files
- `check-secrets.py` hook scans all Edit/Write operations for these patterns
- **What /review should flag:** hardcoded credentials, missing input validation,
  SQL injection vectors, XSS in templates, insecure HTTP headers

## Dependency Policy

- Pin exact versions in `package.json` (no `^` or `~`)
- Review changelogs before upgrading major versions
- No dependencies with known critical CVEs
- Prefer well-maintained packages with active communities

## Permission Mode

**Mode:** `default`

**Justification:** Default mode provides the best balance for a governed pipeline:
- Prompts for potentially dangerous operations (giving hooks a chance to block)
- Allows read operations freely for code analysis
- Hook system adds a second layer of validation on top of permission prompts
- Enterprise projects should use `plan` mode; personal projects can use `auto`
  with hooks as the safety net

## Cost Policy

Cost controls prevent runaway sessions and ensure budget predictability.

- **--max-budget-usd:** Set per session; recommended $5 for normal tasks, $15 for /ship runs
- **--max-turns:** Limit to 50 turns for standard tasks, 100 for /ship pipelines
- **Model selection:** Use `claude-sonnet-4-20250514` for routine tasks (review, test-gen, commit);
  reserve `claude-opus-4-20250115` for complex architectural decisions only
- **Cost logging:** `session-summary.sh` stop hook records tokens used per session to `costs.jsonl`
- **Weekly budget:** Track cumulative spend; alert if >$50/week/developer

## What /review Should Flag

Beyond security issues listed above, `/review` must check for:
- Violations of commit format conventions
- Functions exceeding 40 lines
- Missing error handling on async operations
- Unused imports or variables
- `var` usage (should be `const` or `let`)
- Missing test coverage for new code paths
- Hardcoded magic numbers without named constants
- Console.log statements left in production code
