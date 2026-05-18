# ADR-002 — Stats Computation Strategy

## Status

Accepted — 2026-05-18

## Context

REQ-007 introduces GET /api/notifications/stats returning total, by_type, by_status, and last_sent. Two implementation strategies were considered: (1) compute on-demand from the history list, (2) maintain counter dicts updated incrementally on every send. The service uses in-memory stores with MAX_HISTORY=100, so the total dataset size is bounded.

The stats endpoint is read-only and does not trigger the email provider or modify state. It must handle records where the `type` field is null without raising an exception (REG-006 regression case).

## Decision

Compute stats on-demand from `_notification_history` via a single pass in `NotificationService.get_stats()`. Each call iterates the list (at most 100 records), aggregating `by_type` and `by_status` counters and tracking the maximum timestamp for `last_sent`. Null-type records are mapped to `"unknown"` via `record.get("notif_type") or record.get("type") or "unknown"`.

## Alternatives Considered

1. **Incremental counters** — maintain `_by_type_counter`, `_by_status_counter`, and `_last_sent_timestamp` as module-level state, updated inside `_record_history`. Rejected because it duplicates state (the history list already has the truth), requires invalidation logic when history is rotated past MAX_HISTORY, and introduces a class of consistency bugs the on-demand computation cannot have.

2. **External cache (Redis)** — out of scope; the project explicitly uses in-memory stores only.

3. **Lazy computation with TTL cache** — premature optimization for 100 or fewer records; adds dependency surface (cachetools or similar) for negligible benefit.

## Consequences

**Positive:**
- Single source of truth (the history list)
- No invalidation bugs when records are evicted at MAX_HISTORY
- Trivial null-type resilience via defensive `.get()` with fallback
- Test surface is small: 5 unit cases + 5 integration cases + 1 regression case cover the behavior fully

**Negative:**
- O(n) per call, where n is at most MAX_HISTORY (100). For the current scale this is negligible (under 1ms). If MAX_HISTORY grows to 10K+ or the endpoint becomes hot, revisit with incremental counters or caching.

**Neutral:**
- The stats endpoint is unauthenticated, consistent with other read endpoints in this service. Out of scope for this ADR; flagged for a future ADR if the service is exposed externally.
