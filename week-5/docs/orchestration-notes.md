# Orchestration Notes — Composing Skills into Pipelines

Forward-looking design notes for an Orchestrator step that composes the
two existing Skills (`architecture-review`, `security-audit`) into a
single, action-oriented pipeline. **Not implemented in v1.0.0.** Sketched
here so the next iteration has a concrete starting point.

---

## Sequential pattern (current pipeline)

```
{{TARGET}} ──► architecture-review ──► design.md
                                            │
{{TARGET}} ──► security-audit ──── design.md ──► findings.json
```

The Architect runs first; its `design.md` becomes optional context for
the Security Agent. Security Agent never re-runs Architect's analysis —
it consumes the design as boundary information only.

**Strengths:**
- Each agent's output is independently reviewable.
- Hand-off contract is small (one markdown file).
- `design.md` gives Security Agent immediate boundary clarity (which
  functions are public, where data crosses module edges).

**Weaknesses:**
- Strictly serial. Security Agent waits for Architect to finish.
- A bug in `design.md` (e.g. a misidentified public function) propagates
  silently into the Security Agent's framing.

---

## Parallel pattern (alternative)

```
{{TARGET}} ──┬─► architecture-review ──► design.md ────┐
             │                                          │
             └─► security-audit ──► findings.json ──────┴─► Orchestrator ──► action_plan.md
```

Both agents run in parallel, then an Orchestrator reconciles their
outputs.

**Strengths:**
- Faster wall-clock time on long-running agents.
- Security findings cannot be biased by a flawed `design.md`.

**Weaknesses:**
- Security Agent loses the boundary context, so over-flags (every
  function looks suspicious without knowing which are internal helpers).
- Orchestrator must resolve contradictions: e.g. Architect says
  `_call_stripe_api` is delegated; Security flags it as an internal
  function with a missing input check. Both can be right; the
  Orchestrator decides which framing the action plan adopts.

---

## Sample Orchestrator prompt (concrete, not run)

Save as `skills/orchestrator/SKILL.md` if/when implemented:

```
ROLE
You are a senior staff engineer. You triage the outputs of an Architect
Agent and a Security Agent into a single action plan that an
implementation engineer can execute in one PR.

SCOPE
{{DESIGN}} + {{FINDINGS}} only. You do not re-read source code; you trust
the two agents' file:line references.

EXCLUSIONS — DO NOT do any of the following:
- DO NOT add new findings the upstream agents did not produce.
- DO NOT downgrade severities; only re-categorise (a "high" stays "high"
  unless the Architect's design.md proves the function is unreachable
  from any external caller, in which case downgrade to "info").
- DO NOT propose code; only describe the change in 1 sentence per item.

INPUT
- {{DESIGN}}: full content of design.md
- {{FINDINGS}}: full content of findings.json

OUTPUT FORMAT
A single markdown document with three numbered sections:

## MUST_FIX (anything critical or high in findings.json that touches
a public function per design.md)
1. [file:line] — short title. Why it must fix: 1 sentence pulling from
   findings.json `impact`. Recommended: 1 sentence pulling from
   `recommendation`.

## SHOULD_FIX (medium severity, OR critical/high on internal helpers)
2. [file:line] — same shape as MUST_FIX.

## NICE_TO_HAVE (low / info)
3. [file:line] — same shape.

End with: "## ARCHITECTURAL CONTEXT" — 2 sentences quoting the Architect's
SUMMARY and saying which findings, if any, are direct consequences of
the architectural concern.

No preamble. No explanation outside this format.
```

---

## Hand-off contract between Skills (in/out)

| Skill | Required input | Output | Consumed by |
|---|---|---|---|
| `architecture-review` | `{{CONTEXT}}` (CLAUDE.md), `{{TARGET}}` (source) | `design.md` (4 sections + SUMMARY) | `security-audit` (optional context), `orchestrator` (required) |
| `security-audit` | `{{CONTEXT}}`, `{{TARGET}}`, optionally `{{DESIGN}}` | `findings.json` (summary + finding objects) | `orchestrator` (required), CI gate |
| `orchestrator` (proposed) | `{{DESIGN}}`, `{{FINDINGS}}` | `action_plan.md` (MUST_FIX / SHOULD_FIX / NICE_TO_HAVE) | Human reviewer |

The contract pattern is: each Skill's output is structured enough that
the next Skill can parse it without re-reading source. This is what
makes composition possible — the Orchestrator never re-runs the
Architect or the Security Agent; it just reconciles their two
documents.

---

## Why the Orchestrator is deferred to v1.1.0+

Three reasons to *not* build the Orchestrator now:

1. **One real composition use case is needed before designing the
   contract.** With only OrderFlow as a target, the Orchestrator's
   merge logic would be designed speculatively. Better to wait until
   a second project produces a `design.md` + `findings.json` pair
   that doesn't fit the OrderFlow shape, then design the Orchestrator
   against the actual variation.
2. **The hand-off contract is the hard part.** A bad Orchestrator
   schema locks in for v2.0.0+ migrations forever. v1.0.0 of the
   contract should be designed against ≥2 real input pairs.
3. **Parallel pattern's tradeoff is unclear without measurement.**
   Wall-clock improvement vs. quality regression on Security Agent
   over-flagging needs real numbers, not estimates. Defer until
   parallel can be A/B'd against sequential.

The above is intentional under-engineering — the v1.0.0 Skills library
is a working two-agent pipeline that ships. The Orchestrator is on
the v1.1.0 backlog with a concrete starting prompt and a clear
trigger condition (a second real project worth of pipeline output).
