# /test-gen — Test Generation

Generate vitest tests for changed files, run them, and report coverage.

## Instructions

1. Identify changed files by running `git diff --name-only` (or `git diff --cached --name-only` for staged changes). Filter to source files only (`.ts`, `.js` in `src/` or `routes/` or `lib/`).

2. For each changed source file, read its contents and generate a vitest test file that covers:
   - **Happy path:** at least 2 tests for normal/expected usage
   - **Error cases:** at least 2 tests for invalid input, missing data, or failure scenarios
   - **Edge cases:** at least 1 test for boundary conditions (empty input, max length, concurrent access, expired data)

3. Follow these testing conventions from `week-3/CLAUDE.md`:
   - Use `describe`/`it`/`expect` from vitest
   - Test file naming: `<module>.test.ts` in a `tests/` directory
   - Each test must be independent — no shared mutable state
   - Mock only external dependencies; use real in-memory store
   - Include REQ-ID traceability comments where applicable (`// TESTS: REQ-SHORT-00N`)

4. Write or update the test files in the appropriate location.

5. Run the tests with coverage:
   ```bash
   cd week-3/sample-target && npx vitest run --coverage 2>&1
   ```

6. Capture the full output (pass/fail results + coverage table) and write it to:
   ```
   week-3/.claude/audit/test-gen-sample-output.txt
   ```

7. Output a summary:
   ```
   ## Test Generation Summary
   - Files analyzed: N
   - Tests generated: N
   - Tests passing: N / N
   - Coverage: N% lines
   - Output saved to: week-3/.claude/audit/test-gen-sample-output.txt
   ```

8. If any test fails, report the failure details. The `/ship` pipeline will abort if tests fail.
