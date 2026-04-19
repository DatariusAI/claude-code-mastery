# /commit — Smart Commit Message

Analyze the staged diff and produce a Conventional Commit message.

## Instructions

1. Run `git diff --cached --stat` to see which files are staged and the scope of changes.

2. Run `git diff --cached` to read the actual diff content.

3. Analyze the changes and determine:
   - **Type:** one of `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
     - `feat` = new feature or capability
     - `fix` = bug fix
     - `docs` = documentation only
     - `style` = formatting, no logic change
     - `refactor` = code restructuring, no behavior change
     - `test` = adding or updating tests
     - `chore` = build, CI, config, dependency updates
   - **Scope:** derived from the primary changed directory or module (e.g., `routes`, `hooks`, `commands`, `audit`)
   - **Summary:** imperative mood, lowercase, no period, max 72 chars

4. Generate the commit message in this format:
   ```
   type(scope): imperative summary

   Body explaining what changed and why (not how).
   Reference any relevant REQ-IDs, issue numbers, or
   hook/command names affected.
   ```

5. Stage any unstaged but related files if needed (ask first).

6. Run the commit:
   ```bash
   git commit -m "<generated message>"
   ```

7. Report the commit hash and message.

## Examples

```
feat(routes): add soft delete endpoint for short URLs

Implements REQ-SHORT-006 with soft delete semantics.
Sets is_active=false instead of removing the record,
allowing future restoration and audit trail.
```

```
test(shorten): add edge case tests for duplicate detection

Covers SCEN-005 with timestamp-unique URLs to prevent
false positives from test isolation issues.
```
