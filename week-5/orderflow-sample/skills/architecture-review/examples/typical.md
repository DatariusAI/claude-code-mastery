## 1. Module Boundary

This module owns the orchestration of payment lifecycle operations — charge creation with retry semantics, refund issuance, transaction persistence, and payment history retrieval — for the OrderFlow backend. It delegates the actual Stripe HTTP transport to `_call_stripe_api` (currently stubbed) and database execution to `_execute_query` (currently stubbed), meaning the module owns the *policy* (retry counts, backoff curve, payload shape, SQL composition) but not the *mechanism* of either external integration. Cross-boundary concerns such as authentication, authorization, webhook reconciliation, and notifications are explicitly outside this module's responsibility and live in sibling modules.

Public functions:
- `process_payment(amount, currency, card_token, user_id)`
- `record_transaction(user_id, amount, charge_id)`
- `refund_payment(charge_id, amount=None)`
- `get_payment_history(user_id)`

Internal helpers:
- `_call_stripe_api(payload, endpoint="charges")`
- `_execute_query(query)`

## 2. API Surface

| Function | Inputs | Outputs | Side effects |
|---|---|---|---|
| `process_payment` | `amount` (int/float, untyped), `currency` (str), `card_token` (str), `user_id` (str/int) | `dict` with keys `success: bool`, `charge_id: Optional[str]`, `error: Optional[str]` | Calls Stripe via `_call_stripe_api`; writes a transaction row via `record_transaction`; emits error logs; sleeps via `time.sleep` between retries (blocking) |
| `record_transaction` | `user_id`, `amount`, `charge_id` | None (implicit) | Executes a raw SQL INSERT against the `transactions` table; emits info log containing the full query |
| `refund_payment` | `charge_id` (str), `amount` (Optional, default `None` = full refund) | Raw return value of `_call_stripe_api` (a `dict` with `id`) | Calls Stripe `refunds` endpoint |
| `get_payment_history` | `user_id` | Raw DB rows (list) | Executes a raw SQL SELECT against the `transactions` table |

## 3. Data Flow

1. Caller invokes `process_payment(amount, currency, card_token, user_id)`. No validation occurs on inputs — amount, currency, or token shape are accepted as-is.
2. A `payload` dict is constructed in-memory, embedding `user_id` inside Stripe `metadata`.
3. A retry loop begins, bounded by module-level constant `MAX_RETRIES` (3).
4. **External API call**: `_call_stripe_api(payload)` is invoked inside a broad `try` block catching all `Exception`.
5. On success, **DB write** occurs: `record_transaction(user_id, amount, charge["id"])` synchronously executes an INSERT before the function returns. The Stripe call and DB write are not transactional with respect to each other — a DB failure after a successful charge will surface as a generic exception and re-enter the retry loop, potentially double-charging.
6. On success path, function returns `{"success": True, "charge_id": charge["id"], "error": None}`.
7. **Retry point**: on any exception, the failure is logged and `time.sleep(2 ** attempt)` blocks the calling thread (1s, 2s, 4s) before the next attempt. No jitter, no idempotency key passed to Stripe across retries.
8. After `MAX_RETRIES` exhausted attempts, function returns `{"success": False, "charge_id": None, "error": "Max retries exceeded"}` — the original exception detail is dropped from the return value (only present in logs).

## 4. Dependencies

External dependencies (beyond stdlib + typing):
- None. The module currently imports only `time`, `logging`, and `typing.Optional`. Real Stripe SDK / HTTP client and DB driver are absent (stubbed).

Internal dependencies (other modules in the repo):
- None imported. However, `record_transaction` and `get_payment_history` produce/consume rows in a `transactions` table whose schema is implicitly shared with any other module reading payment data (e.g. `payments/webhook.py` per the module map). This is a coupling via shared database state, not via code import — an undeclared contract.

Hidden dependencies:
- `STRIPE_API_KEY` — module-level constant, hardcoded placeholder, not actually consumed by `_call_stripe_api` (dead reference).
- `MAX_RETRIES` — module-level constant; not configurable per-call or per-environment.
- `logger` — module-level singleton bound to `__name__`; logging configuration is inherited from whatever process imports this module.
- Implicit DB connection / session — `_execute_query` presumes an ambient connection that is not visible in this module's signature surface.
- Implicit `transactions` table schema — column order is positional in the INSERT, so the module is coupled to a specific `(user_id, amount, charge_id)` column ordering defined elsewhere.

## SUMMARY

This module is the policy layer for OrderFlow's payment lifecycle, sitting between callers and two stubbed integration points (Stripe and the database) and owning retry, payload shaping, and persistence orchestration. The biggest architectural concern is the lack of transactional boundary between the external charge call and the local DB write inside `process_payment` — combined with a blanket-`except` retry loop that has no idempotency key, the module can silently produce duplicate charges or charge-without-record states whenever the post-charge DB write fails.
