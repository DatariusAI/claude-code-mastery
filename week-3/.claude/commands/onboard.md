# /onboard — New Hire Onboarding

Generate an architecture summary for new team members joining this project.

## Instructions

1. Read the following files to build a comprehensive understanding:
   - `week-3/CLAUDE.md` — project conventions and rules
   - `week-3/README.md` — project overview and structure
   - Source files in `week-3/sample-target/src/` — the codebase being governed
   - `week-3/.claude/settings.json` — active hooks and permissions

2. Produce a structured onboarding document with these sections:

   ### Project Overview
   Brief description of what the project does, its purpose, and the tech stack.

   ### Architecture Map
   ```
   Key directories and their purpose:
   src/index.ts          — App entry point, route registration, error handlers
   src/routes/           — HTTP route handlers (shorten, redirect, delete, analytics)
   src/lib/store.ts      — In-memory data store (urls Map, analytics array)
   src/lib/validator.ts  — URL validation and blocklist checking
   src/lib/shortener.ts  — Short code generation (6-char alphanumeric)
   src/types.ts          — TypeScript interfaces (UrlRecord, ErrorResponse, etc.)
   tests/                — Vitest test files (one per route/module)
   ```

   ### Key Files and Their Purpose
   For each source file, list: path, purpose, key exports, which REQ-IDs it implements.

   ### Naming Conventions
   - File naming patterns
   - Variable/function naming (camelCase, PascalCase for types)
   - Test file naming (`<module>.test.ts`)
   - Commit message format

   ### Testing Patterns
   - Framework: Vitest
   - How tests are structured (describe/it/expect)
   - How the Hono app is tested (app.request pattern)
   - Coverage requirements (80% minimum)

   ### Non-Obvious Invariants
   Things a new developer might not realize:
   - Route registration order matters (specific paths before `/:code` wildcard)
   - Store uses in-memory Maps (no persistence across restarts)
   - `deleteByCode` is a soft delete (sets `is_active = false`)
   - Short codes are 6 chars, alphanumeric, checked for collisions
   - Blocklist is hardcoded in validator (not configurable at runtime)
   - Tests import the app directly (no server startup needed for testing)

   ### Governance Layer
   - Active hooks and what they block
   - How to run the pipeline (`/ship`)
   - Where audit logs are stored
   - What permission mode is set and why

   ### Getting Started
   Step-by-step for a new developer:
   1. Clone the repo
   2. Read CLAUDE.md
   3. `cd week-3/sample-target && npm install`
   4. `npx vitest run` to verify tests pass
   5. Make a small change and run `/ship` to experience the pipeline

3. Output the document as clean markdown suitable for a team wiki or Notion page.
