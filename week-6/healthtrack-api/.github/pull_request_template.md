## Summary
<!-- What does this PR do? One or two sentences. -->

## Changes Made
<!-- List the files changed and why -->
- 
- 

## Breaking Changes
<!-- Does anything break? API changes, DB migrations, env var changes? -->
- [ ] No breaking changes
- [ ] Breaking change — describe below:

## Testing
<!-- How was this tested? -->
- [ ] `pytest tests/` passes locally
- [ ] `docker compose up` works and `/health` returns 200
- [ ] Manual testing: 

## Security
<!-- Any security considerations? -->
- [ ] No secrets added to source code
- [ ] No hardcoded credentials

## Performance Impact
<!-- Will this change request latency, memory, or DB load? -->
- [ ] No measurable impact on hot paths (`/vitals`, `/alerts`)
- [ ] New queries are indexed; no N+1 patterns introduced
- [ ] If perf-sensitive: before/after numbers in the description

## Database Migrations
<!-- Schema changes need to be safe to roll forward AND backward. -->
- [ ] No migration in this PR
- [ ] Migration is reversible and has a `down` step
- [ ] Migration has been tested on a copy of production data

## Feature Flags
<!-- New behaviour should be flag-gated until validated. -->
- [ ] No new behaviour requiring a flag
- [ ] Flag added with a default that preserves current behaviour
- [ ] Flag is documented in `.env.example` and `CLAUDE.md`

## Deployment Notes
<!-- Anything ops needs to know? New env vars? DB migrations? -->

## Checklist
- [ ] Code reviewed by at least one team member
- [ ] Tests added or updated
- [ ] CLAUDE.md updated if project context changed
- [ ] .env.example updated if new env vars added
