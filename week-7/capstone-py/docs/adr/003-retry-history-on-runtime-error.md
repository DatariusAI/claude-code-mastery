# ADR-003 — Retry History on RuntimeError

## Status

Accepted — 2026-05-18

## Context

When all retry attempts are exhausted in `NotificationService.send()`, the service must communicate both the failure and the history of each attempt (attempt number, error message, timestamp) to the caller. The route handler serializes this into a 500 response with `retry_history` in the JSON body.

Three approaches were considered for how the service layer communicates retry history to the route layer.

## Decision

Raise a standard `RuntimeError` and attach `retry_history` as a dynamic attribute on the exception object after construction:

```python
error = RuntimeError(f"Failed to send notification after {max_retries} attempts")
error.retry_history = retry_history  # type: ignore[attr-defined]
raise error
```

The route handler accesses `e.retry_history` in its `except RuntimeError as e:` block.

## Alternatives Considered

1. **Custom `NotificationFailedError(Exception)` class** with `retry_history` as a constructor argument. This is the most type-safe approach and eliminates the `# type: ignore` annotation. Rejected for this project because it adds a class definition for a single use site, and the scaffold's existing pattern already uses `RuntimeError` consistently for all service-layer failures. Introducing a custom exception would break the existing error-handling contract without adding meaningful behavioral differentiation.

2. **Return a result dict** `{"success": False, "retry_history": [...]}` instead of raising. Rejected because it changes the control flow contract — callers must check a boolean instead of catching exceptions, which is error-prone and inconsistent with the rest of the service's raise-on-failure pattern.

3. **Log retry_history and raise a bare RuntimeError** without attaching the history. The caller would only get the error message, not the structured attempt data. Rejected because the 500 response body is specified to include `retry_history` (REQ-002 acceptance criteria), and the audit trail alone is not sufficient for the API consumer.

## Consequences

**Positive:**
- Zero additional classes or dependencies
- Consistent with the scaffold's existing RuntimeError pattern
- retry_history is directly available to the route handler for serialization
- The 500 response body includes structured attempt data per REQ-002

**Negative:**
- Dynamic attribute assignment requires `# type: ignore[attr-defined]` for mypy/pyright — a type-checking caveat that is already present in the code and documented in this ADR
- If another exception handler catches the RuntimeError upstream without checking for `retry_history`, the attribute may go unused (defense: the route handler is the only caller)

**Neutral:**
- If the project later needs multiple custom exception types (e.g., `ValidationError`, `RateLimitError`), a custom exception hierarchy would be warranted and this decision should be revisited
