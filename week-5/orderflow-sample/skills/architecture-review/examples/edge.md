## 1. Module Boundary

`payments/webhook.py` is the inbound integration boundary between Stripe (external system) and the OrderFlow payments domain. Its single responsibility is to receive raw HTTP webhook payloads, authenticate them as originating from Stripe, decode the event envelope, and dispatch to a per-event-type handler resolved via an in-process registry. It owns neither the HTTP transport (no framework binding — it consumes already-extracted `bytes` and a header string) nor the downstream business logic (handlers are registered by other modules, or co-located stubs in this file). It does not touch persistence, queues, or `payments/processor.py` directly; coupling to the rest of the payments domain happens implicitly through whatever functions decorate themselves with `@register_handler`.

## 2. API Surface

| Function | Inputs | Outputs | Side effects |
|---|---|---|---|
| `handle_webhook` | `request_body: bytes`, `signature_header: str` | `dict` (`{"status": "ok"}`) | Reads module-global `WEBHOOK_SECRET` and `EVENT_HANDLERS`; raises `ValueError` on signature mismatch; invokes registered handler (arbitrary side effects); emits `logger.info` / `logger.warning`; lazy-imports `json` on every call |
| `register_handler` | `event_type: str` | Decorator returning the original function unchanged | Mutates module-global `EVENT_HANDLERS` dict at import time |
| `on_charge_succeeded` | `event: dict` | `None` (implicit) | Emits `logger.info`; registered into `EVENT_HANDLERS["charge.succeeded"]` as an import-time side effect |
| `on_charge_failed` | `event: dict` | `None` (implicit) | Emits `logger.error`; registered into `EVENT_HANDLERS["charge.failed"]` as an import-time side effect |

## 3. Data Flow

1. Caller invokes `handle_webhook(request_body, signature_header)` with the raw HTTP body and the Stripe signature header value.
2. `WEBHOOK_SECRET` (module constant) is encoded to bytes and concatenated with `request_body`; an MD5 digest is computed as `expected`.
3. `signature_header` is compared against `expected` via `!=`; on mismatch a `ValueError("Invalid webhook signature")` is raised and propagates to the caller, terminating the flow.
4. `json` is imported lazily inside the function, and `request_body` is parsed via `json.loads` into `event` (no try/except — a malformed body raises `json.JSONDecodeError` to the caller).
5. `event_type` is read via `event.get("type")` (no schema validation; `None` is a legal lookup key).
6. `EVENT_HANDLERS.get(event_type)` resolves a handler from the module-global registry populated at import time by `@register_handler` decorators.
7. If a handler is found, it is invoked synchronously with the full `event` dict; its return value is captured as `result` and logged at INFO with the event type. If no handler is found, a WARNING is logged and dispatch is skipped silently.
8. `handle_webhook` returns `{"status": "ok"}` to the caller — unconditionally on the dispatch path, regardless of handler outcome (including `None` returns or handler-raised exceptions, which would actually escape before reaching this line).

## 4. Dependencies

**External (third-party / stdlib):**
- `hashlib` — MD5 digest computation for signature check.
- `logging` — module logger named `payments.webhook`.
- `json` — stdlib, imported lazily inside `handle_webhook` rather than at module top.
- `typing.Callable`, `typing.Dict` — type hints for the registry.

**Internal (OrderFlow):**
- None imported directly. The contract surface is the `@register_handler` decorator, which other OrderFlow modules (e.g., `payments/processor.py`) are expected to call to attach domain logic. There is currently no import edge to `processor.py`, `auth/auth.py`, or `notifications/notifier.py` in this file.

**Hidden / implicit:**
- `WEBHOOK_SECRET` — declared as a module-level string literal with a placeholder value; the comment acknowledges it should come from an env var. The dependency on configuration is real but unwired.
- `EVENT_HANDLERS` — module-global mutable state; correctness of dispatch depends on import order of any module that registers handlers. If a registering module is never imported, its events silently fall through to the WARNING branch.
- Caller contract — `handle_webhook` assumes the HTTP layer has already extracted the raw body as `bytes` (not re-serialized) and passed the `Stripe-Signature` header verbatim; any framework that mutates the body before this point breaks the signature step.
- Stripe event schema — handlers index into `event["data"]["object"]` and `charge["id"]`, `charge["amount"]`, an undocumented contract with the Stripe payload shape that is not validated at the boundary.

## SUMMARY

`webhook.py` is a thin, framework-agnostic dispatcher whose contract is `(bytes, str) -> dict`, gated by a signature check and routed through an import-time-populated handler registry. Its real coupling to the rest of OrderFlow is invisible at this file's import graph and lives entirely in the `EVENT_HANDLERS` global, which makes the module's behavior a function of which other modules happen to have been imported.
