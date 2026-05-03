# Skill: architecture-review
# Version: 1.0.0
# Status: draft
# Owner: orderflow-engineering
# Category: code-quality
# Created: 2026-05-03

---

## Purpose

Produces a structured architectural review of a single Python module — boundary,
public API surface, runtime data flow, and declared / hidden dependencies — without
touching security, tests, or refactor proposals. Use this Skill before code review
on a new module that lacks documentation, when onboarding to an unfamiliar module,
or when capturing a frozen architectural snapshot before a planned refactor. The
output is a markdown document with four numbered sections plus a 2-sentence
summary, intended to drop straight into a PR description or `docs/` folder. The
Skill stays in lane: it does not flag security issues, propose code changes, or
critique tests — those concerns are handled by sibling Skills.

---

## Input

| Parameter | Required | Description |
|---|---|---|
| `SCOPE` | Yes | Path to one Python module to analyse (e.g. `payments/processor.py`). One module per run. |
| `CONTEXT` | Yes | Path to (or contents of) the project's `CLAUDE.md` so the agent has the module map and coding standards. |
| `TARGET` | Yes | Full source of `SCOPE` — passed inline so the agent does not need filesystem access. |

---

## Prompt

```
ROLE
You are a senior software architect with 15+ years of experience in payment
systems and Python backend services. You speak in concrete architectural terms —
boundaries, contracts, flows, dependencies — not in vague generalities.

SCOPE
{{SCOPE}} ONLY. You may reference (but not analyse) other modules only when
describing dependency edges that cross the scope boundary.

FOCUS — what this Skill covers (the OUTPUT FORMAT below is also the focus
contract):
- Module boundary (what's owned vs. delegated)
- Public API surface (function-level signatures + side effects)
- Runtime data flow (the steps a primary public function takes)
- Dependencies (external, internal, hidden / module-level state)

EXCLUSIONS — DO NOT do any of the following:
- DO NOT review or comment on security issues (a separate Security Agent
  handles that).
- DO NOT review test coverage or write test cases.
- DO NOT propose implementation code or refactors.
- DO NOT rewrite the module.
- DO NOT speculate about future features not in the codebase.

INPUT
You will receive:
- {{CONTEXT}}: project CLAUDE.md (project standards and module map)
- {{TARGET}}: full source of {{SCOPE}}
Use ONLY these as your source of truth. Do not invent function names, classes,
or behaviour not present in the inputs.

OUTPUT FORMAT — produce a single markdown document with EXACTLY these four
sections in this order, no preamble, no postamble:

## 1. Module Boundary
- One paragraph: what this module owns vs. what it delegates.
- Bullet list of public functions (signature only).
- Bullet list of internal helpers (functions starting with _).

## 2. API Surface
- Markdown table: | Function | Inputs | Outputs | Side effects |
- One row per public function in {{SCOPE}}.

## 3. Data Flow
- Numbered list of the steps a primary public function takes from entry to return.
- Note where DB writes happen, where external API calls happen, and where
  retries occur.

## 4. Dependencies
- External dependencies (imports beyond stdlib + typing).
- Internal dependencies (other modules in the repo it touches).
- Hidden dependencies (env vars, globals, module-level state).

End with: "## SUMMARY" — exactly 2 sentences describing the module's role and
biggest architectural concern (architectural, not security).

If the module is essentially empty (e.g. a one-line `__init__.py`), state that
explicitly in each section and do NOT invent functions or flows.

No preamble. No explanation outside the specified format.
```

---

## Output Spec

```markdown
## 1. Module Boundary

This module owns the orchestration of payment lifecycle operations and delegates
HTTP transport and DB execution to stubbed helpers. Cross-cutting concerns
(auth, notifications, webhook reconciliation) live in sibling modules.

Public functions:
- `process_payment(amount, currency, card_token, user_id)`
- `record_transaction(user_id, amount, charge_id)`

Internal helpers:
- `_call_stripe_api(payload, endpoint="charges")`
- `_execute_query(query)`

## 2. API Surface

| Function | Inputs | Outputs | Side effects |
|---|---|---|---|
| `process_payment` | amount, currency, card_token, user_id | dict(success, charge_id, error) | Stripe call + DB write + retries |

## 3. Data Flow

1. Caller invokes `process_payment(...)` — no input validation occurs.
2. Payload constructed in-memory.
3. Retry loop bounded by `MAX_RETRIES`.
4. _call_stripe_api invoked inside a broad try/except.
5. record_transaction synchronously writes the INSERT after a successful charge.

## 4. Dependencies

External: stdlib only (time, logging, typing.Optional).
Internal: shared `transactions` table schema (no code import edge).
Hidden: STRIPE_API_KEY constant, MAX_RETRIES, module-level logger, ambient DB connection.

## SUMMARY

This module is the policy layer for the payment lifecycle, sitting between callers and two stubbed integration points. The biggest architectural concern is the lack of a transactional boundary between the external charge call and the local DB write, combined with a blanket-`except` retry loop that has no idempotency key.
```

See `examples/typical.md`, `examples/edge.md`, and `examples/minimal.md`
in this Skill's folder for actual output produced on three different
`{{SCOPE}}` inputs (a moderately-complex module, a different-shape module that
uses decorators and a global registry, and a one-line package marker — the
latter verifies the Skill produces an honest "no content" output rather than
hallucinating).

---

## Limitations

- **Single-module scope only.** The Skill does not analyse cross-module flows;
  for a system-level architectural picture, run it on each module and stitch
  the outputs together manually.
- **Long files (>500 lines) may produce shallow output.** Chunk by class /
  section and re-run.
- **Output quality depends on `CLAUDE.md` being current and accurate.**
  Stale module maps will leak into the Architect's framing of internal
  dependency edges.
- **Does not detect hidden runtime behaviour** (monkey-patching, metaclass
  tricks, dynamic imports controlled by env vars). The agent reads source
  literally and reports what it sees.
- **No security commentary by design.** If your code has a hardcoded secret,
  this Skill will note it as a "hidden dependency" (env var coupling), not
  as a security finding. Pair with `security-audit` for that.

---

## Tests

| Test Run | Input | Expected Output | Actual Output | Pass? |
|---|---|---|---|---|
| 1 — Typical | `payments/processor.py` | 4 sections + SUMMARY; identifies retry loop, DB write, hidden deps; zero security commentary | All 4 sections present, SUMMARY surfaces non-transactional charge+write as biggest architectural concern (correctly framed as architectural, not security); zero security commentary leaked | ✅ |
| 2 — Edge case | `payments/webhook.py` | 4 sections + SUMMARY; correctly identifies the `EVENT_HANDLERS` global registry as a hidden dep and the import-time decorator side effects as data flow; stays in lane (does not flag MD5 signature as security) | All 4 sections present, correctly surfaces import-time `EVENT_HANDLERS` mutation, lazy `json` import, and Stripe event-schema as hidden contract; stays in lane | ✅ |
| 3 — Minimal | `auth/__init__.py` (one comment line) | Honest "no content" output; no hallucinated functions; SUMMARY notes it is a passive package marker | Each section explicitly states no content, API Surface table has a `_(none)_` row, SUMMARY correctly identifies the file as a passive package marker deferring to `auth/auth.py` | ✅ |

See `examples/{typical,edge,minimal}.md` for the full outputs.

---

## Changelog

### v1.0.0 — 2026-05-03
- Initial release.
- Tested on: OrderFlow sample repo (`payments/processor.py`, `payments/webhook.py`, `auth/__init__.py`).
- Tested by: orderflow-engineering.
