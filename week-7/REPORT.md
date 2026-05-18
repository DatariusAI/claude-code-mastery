# Capstone Report — Notification Service API

## Submission notes

### 1. What was the most important thing you had to change in Claude's generated code — and why?

The most important change was in the security review's framing rather than the implementation itself. The scaffold shipped REQ-007's `get_stats()` with a working null-type guard (`record.get("notif_type") or record.get("type") or "unknown"`), so the code was already correct. What Claude's initial review missed was surfacing the unauthenticated stats endpoint as a design observation worth documenting. Forcing the review to produce at least two structured findings — the missing auth on `/stats` and the O(n) computation bounded by MAX_HISTORY — transformed a generic "looks clean" response into the kind of output ADR-002 could reference. The spec block for REQ-007 was also absent from `feature_spec.yaml` despite the code being implemented, which is itself a gap the spec-driven workflow caught.

### 2. What did writing the YAML spec before coding change about how you worked?

The spec made the test boundaries obvious. The 6 acceptance criteria in REQ-007 mapped directly to 5 unit test cases and 5 integration test cases — each criterion became a test name. The null-type acceptance criterion forced the REG-006 regression test to exist: without that line in the spec, there would have been no prompt to generate `test_stats_handles_null_type_gracefully`. The spec also made ADR-002's decision section concrete — "compute on-demand from _notification_history" is a sentence that traces back to the "total reflects the count of records in notification history" criterion, not an arbitrary implementation choice. This is the W2 spec-driven workflow paying forward: the YAML spec is the single source that tests, code, and ADRs all reference.

### 3. Which of the 6 sessions' techniques did you use most today? Give an example.

The spec-driven workflow from Week 2 was the most-used technique across the capstone. Every REQ-007 artifact — the YAML block, the implementation verification, the test cases, ADR-002, and the security review — traces back to the spec's acceptance criteria. Concrete example: ADR-002 cites the null-type criterion as the justification for `record.get("type") or "unknown"` over `record["type"]`. The Week 3 governance hook pattern was the second most-used: the pre-commit hook adapted from `.hooks/pre-commit` runs flake8 and unit tests on every commit touching `week-7/capstone-py/`, with a JSONL audit log entry proving the gate fired. The first audit entry was created during Session C's trial commit.

### 4. What would you do differently if you had 30 more minutes?

Three concrete improvements: (1) Add a rate limit decorator to the `/stats` endpoint and a third ADR explaining the threat model — the endpoint is currently unauthenticated and unbounded, which is acceptable for an internal service but would need rate limiting before external exposure. (2) Replace the in-memory `_sent_message_ids` set in `notification_service.py` with a TTL-bounded structure so it doesn't grow unbounded over the container's lifetime — this is a real bug the scaffold has that the security review flagged at LOW severity. (3) Add an integration test that exercises the SIGTERM shutdown path by sending SIGTERM to the running Flask process and asserting it exits cleanly within 2 seconds, rather than relying solely on the signal handler registration check in `run.py`.

## Rubric self-assessment

Per the lab brief's 100-point + 10-point bonus rubric:

| # | Deliverable | Verification | Points | Self-assessed |
|---|-------------|--------------|--------|---------------|
| 1 | pytest — all suites pass | `pytest -q` → 73 passed | 15 | **15** |
| 2 | Coverage >= 80% | `pytest --cov=src` → 96% | 10 | **10** |
| 3 | REQ-007 endpoint works | `curl /api/notifications/stats` → 200 | 15 | **15** |
| 4 | Docker health check passes | `docker-compose up` + `docker inspect` → healthy | 15 | **15** |
| 5 | Governance audit log populated | `curl /api/notifications/audit` → 200 | 10 | **10** |
| 6 | ADR-002 written | `docs/adr/002-stats-computation-strategy.md` | 10 | **10** |
| 7 | metrics-report.md updated | REQ-007 row in both tables | 10 | **10** |
| 8 | Pre-commit hook installed | trial commit fires hook + writes audit | 10 | **10** |
| 9 | Submission notes completed | this REPORT.md | 5 | **5** |
|   | **Subtotal** | | **100** | **100** |
| 10 | Bonus: Second ADR | ADR-003 retry-history-on-runtime-error | +5 | **+5** |
| 11 | Bonus: Docker memory limit | `mem_limit: 256m` in docker-compose.yml | +5 | **+5** |
|   | **Total with bonus** | | **110** | **110** |

Session references:
- Items 1-2 verified in Session B (CI coverage gate PR)
- Item 3 verified live in Session A (curl) and Session C (Docker container)
- Items 4, 5 verified in Session C (Docker live validation)
- Items 6, 7, 8, 10, 11 delivered in Session C
- Item 9 — this file (Session D)

## ROI measurement

Per the lab brief's "ROI Measurement — Fill In Your Numbers" framework. Honest estimates from the actual session runs:

| Phase | Manual estimate | AI-assisted actual | Time saved |
|-------|-----------------|--------------------|------------|
| Spec writing (YAML + Claude review) | 45 min | 5 min | 40 min |
| Implementation (get_stats + route) | 60 min | (already in scaffold) | n/a |
| Unit test writing | 90 min | 8 min | 82 min |
| Integration test writing | 60 min | 8 min | 52 min |
| Regression test writing | 45 min | 5 min | 40 min |
| CI/CD pipeline update | 30 min | 3 min | 27 min |
| Docker build + validation | 45 min | 12 min | 33 min |
| ADR + metrics report | 90 min | 20 min | 70 min |
| **TOTAL** | **~7 hours** | **~1 hour** | **~85%** |

Honest caveats:
- The scaffold ships REQ-007 already implemented; the "Implementation" row is flagged n/a rather than fabricated.
- "AI-assisted actual" includes time spent reading Claude's output, correcting it, and verifying it — not raw generation time.
- 85% time saved is consistent with the program's W6 baseline (~78%) adjusted upward because the spec was the strongest in any week.

## Demo checklist (Phase 7 from lab brief)

All 10 demo items from the lab brief's "Live Demo Checklist":

| Done | Demo item | Command / evidence | Session |
|------|-----------|--------------------|---------|
| Yes | Health check live | `curl /api/health` → 200 | C |
| Yes | Send welcome notification | `curl POST /send {welcome}` → 200 + message_id | C |
| Yes | Send to fail@test.com (retry + 500) | `curl POST /send {fail@test.com}` → 500 + retry_history | C |
| Yes | Show validation error | `curl POST /send` missing `to` → 400 + error | C |
| Yes | Notification history + status filter | `curl /api/notifications?status=success` → 200 + array | C |
| Yes | Governance audit log | `curl /api/notifications/audit` → 200 + audit_log | C |
| Yes | New REQ-007 stats endpoint | `curl /api/notifications/stats` → 200 + stats | A + C |
| Yes | Pre-commit hook output | trial commit in Session C fired hook + wrote audit | C |
| Yes | CI pipeline stages | `.github/workflows/ci.yml` documented in Session B PR | B |
| Yes | Docker health check | `docker inspect ... .State.Health.Status == healthy` | C |

## Inheritance map — what came from prior weeks

This capstone is the integration of every prior week's technique. Concrete examples in the final artifact:

| From | Technique | Where it shows up |
|------|-----------|-------------------|
| W2 | Spec-driven workflow + REQ-ID traceability | `feature_spec.yaml` REQ-007, REQ-IDs in docstrings |
| W3 | Pre-commit hook + JSONL audit log schema | `.git/hooks/pre-commit` adapted from W3 pattern, `.audit-log.jsonl` |
| W4 | Audit middleware + structured error handling | `src/middleware/audit_logger.py`, retry_history attached to RuntimeError |
| W5 | Structured agent prompts | Phase 2 security review prompt format |
| W6 | Multi-stage Dockerfile + 6-stage GitHub Actions CI | `Dockerfile`, `.github/workflows/ci.yml` |

## Reflection — what the program proved

The 7-week program proved that AI does not replace engineering judgment — it compresses the boilerplate-shaped parts of engineering so judgment time scales with the parts that actually need it. The clearest moment in this capstone was the sanitization decision in Session A: the scaffold contained `SECRET_KEY="dev-only-change-in-prod"` which is a clearly-labeled placeholder, not a real secret. The decision to use the W5 pattern (sanitize before first commit) rather than the W6 pattern (leave teaching fixtures for CI to catch) required understanding both patterns and the context that no CI step in this project's pipeline needs intentional secret fixtures to fire. That judgment call — context-dependent, non-obvious, and consequential — is exactly the kind of decision AI generates options for but cannot make. The ROI table shows 85% time savings; the missing 15% is where the judgment lives.
