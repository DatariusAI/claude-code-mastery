# /review — AI Code Review

Review the staged diff against the project's CLAUDE.md conventions. Produce a structured audit of every issue found.

## Instructions

1. Read `week-3/CLAUDE.md` to load the project conventions (commit format, file scope, coverage threshold, dependency policy, security rules, code style).

2. Run `git diff --cached` to get the staged diff. If nothing is staged, run `git diff` for unstaged changes instead.

3. For each changed file in the diff, analyze every hunk and check for violations of:
   - **Security:** hardcoded API keys, passwords, tokens, `sk-ant-` strings, missing input validation, SQL injection, XSS vectors
   - **Code style:** `var` usage (should be `const`/`let`), functions over 40 lines, unused imports/variables, console.log in production code, hardcoded magic numbers
   - **Conventions:** commit message format violations, files outside allowed scope (per scope-guard allowlist), missing REQ-ID traceability comments
   - **Testing:** new code paths without corresponding test coverage, test files not following `<module>.test.ts` naming
   - **Dependencies:** unpinned versions (`^` or `~`), packages with known CVEs

4. For each finding, output a structured entry:

   ```
   ### Finding N
   - **File:** <file path>
   - **Line:** <line number or range>
   - **Severity:** info | warn | error
   - **Rule:** <which CLAUDE.md rule was violated>
   - **Rationale:** <why this is a problem>
   - **Suggested fix:** <concrete code change or action>
   ```

5. After all findings, output a summary:
   ```
   ## Review Summary
   - Errors: N
   - Warnings: N
   - Info: N
   - Verdict: PASS (no errors) | FAIL (errors found)
   ```

6. If any finding has severity `error`, the review verdict is **FAIL**. The `/ship` pipeline will abort on FAIL.

## Example Output

```
### Finding 1
- **File:** src/routes/shorten.ts
- **Line:** 15
- **Severity:** error
- **Rule:** Security — no hardcoded secrets
- **Rationale:** API key string detected in source code
- **Suggested fix:** Move to environment variable, reference via `process.env.API_KEY`

## Review Summary
- Errors: 1
- Warnings: 0
- Info: 0
- Verdict: FAIL
```
