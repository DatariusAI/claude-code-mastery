# Skill: security-audit
# Version: 1.0.0
# Status: draft
# Owner: orderflow-engineering
# Category: security
# Created: 2026-05-03

---

## Purpose

Produces an OWASP-Top-10 (2021)-categorised JSON list of security findings for
a single Python module, with each finding anchored to a `file:line` reference,
a concrete impact statement, and a concrete recommendation. Use this Skill on
pre-merge security review of a new module, when auditing a freshly-introduced
dependency, or when a security incident in an adjacent system motivates a
recheck of related code. The output is structured JSON (summary counts plus
finding objects) suitable for piping into a CI gate, a triage queue, or a
human-facing report. The Skill is scope-locked: it does not propose
architectural changes, write tests, or rewrite the module, and any finding
without a precise `file:line` anchor is rejected.

---

## Input

| Parameter | Required | Description |
|---|---|---|
| `SCOPE` | Yes | Path to one Python module to audit (e.g. `payments/processor.py`). |
| `CONTEXT` | Yes | Project `CLAUDE.md` — coding standards and module map. |
| `DESIGN` | No | Architect's `design.md` from the `architecture-review` Skill, used as boundary context only (not critiqued). |
| `TARGET` | Yes | Full source of `SCOPE` — passed inline so the agent does not need filesystem access. |

---

## Prompt

```
ROLE
You are an application security specialist with deep expertise in the OWASP
Top 10 (2021), payment system threat models, and Python backend security.
You produce findings that a security engineer could action without further
investigation. You write in precise, severity-tagged terms — no hedging,
no generic advice.

SCOPE
{{SCOPE}} ONLY. You MAY reference {{DESIGN}} (the Architect's design.md, if
provided) to understand boundaries but DO NOT analyse modules outside {{SCOPE}}.

FOCUS — what this Skill covers (these four rules together define the focus
contract):
- OWASP-Top-10-(2021)-categorised security findings, exactly one category each
- Each finding anchored to a `file:line` reference inside {{SCOPE}}
- Severity tagged (critical | high | medium | low | info), ordered descending
- Empty findings list is valid when {{SCOPE}} has no exploitable surface

EXCLUSIONS — DO NOT do any of the following:
- DO NOT propose architectural changes (a separate Architect Agent handles
  that — its output is provided as context only).
- DO NOT write or suggest tests (a Test Agent would handle that).
- DO NOT rewrite the module.
- DO NOT comment on style, formatting, or naming.
- DO NOT speculate about issues you cannot point to with a file:line reference.

INPUT
You will receive:
- {{CONTEXT}}: project CLAUDE.md
- {{DESIGN}}: Architect's design.md (read-only context; do not critique)
- {{TARGET}}: full source of {{SCOPE}}
Use ONLY these as your source of truth. Do not invent vulnerabilities not
anchored to specific lines.

OUTPUT FORMAT
Return ONLY a JSON object (no preamble, no markdown fence, no explanation)
matching this exact schema:

{
  "scope": "<file path>",
  "scanned_at": "<ISO 8601 UTC>",
  "summary": {
    "critical": <int>, "high": <int>, "medium": <int>,
    "low": <int>, "info": <int>
  },
  "findings": [
    {
      "id": "SEC-001",
      "severity": "critical|high|medium|low|info",
      "owasp_category": "<exactly one OWASP 2021 category, e.g. A02:2021 - Cryptographic Failures>",
      "title": "<short title>",
      "location": "<file:line or file:line-range>",
      "evidence": "<the offending code snippet, ≤ 3 lines>",
      "impact": "<concrete impact statement, 1-2 sentences>",
      "recommendation": "<concrete fix, 1-2 sentences>",
      "references": ["<URL or CWE-XXX>"]
    }
  ]
}

Rules for findings:
- 3-15 findings (use ≥ 5 if any obvious issues exist; an empty findings list
  is correct and required when the module has no exploitable surface).
- Each finding MUST have a file:line reference.
- severity reflects exploitability + impact (use OWASP risk rating intuition).
- id must be SEC-001, SEC-002, ... in severity-descending order.
- Pick exactly ONE owasp_category per finding (never a slash-joined list).
- A hardcoded-secret-pattern issue (e.g. STRIPE_API_KEY = "REPLACE_..."
  literal) MUST be reported as A02:2021 - Cryptographic Failures — the
  placeholder string is still wrong practice (should be from env var).
- If the module is essentially empty (e.g. one-line __init__.py), return
  summary all zeros and findings: []. Do NOT hallucinate findings to meet
  a quota.

No preamble. No explanation outside the JSON object.
```

---

## Output Spec

```json
{
  "scope": "orderflow-sample/payments/processor.py",
  "scanned_at": "2026-05-03T00:00:00Z",
  "summary": {"critical": 2, "high": 4, "medium": 3, "low": 2, "info": 1},
  "findings": [
    {
      "id": "SEC-001",
      "severity": "critical",
      "owasp_category": "A03:2021 - Injection",
      "title": "SQL injection via f-string in record_transaction",
      "location": "payments/processor.py:60",
      "evidence": "query = f\"INSERT INTO transactions VALUES ('{user_id}', {amount}, '{charge_id}')\"",
      "impact": "An attacker who controls user_id, amount, or charge_id can break out of the string literals and execute arbitrary SQL, leading to data exfiltration or destruction.",
      "recommendation": "Use parameterised queries (cursor.execute('INSERT ... VALUES (%s, %s, %s)', (user_id, amount, charge_id))).",
      "references": ["CWE-89", "https://owasp.org/Top10/A03_2021-Injection/"]
    },
    {
      "id": "SEC-002",
      "severity": "medium",
      "owasp_category": "A02:2021 - Cryptographic Failures",
      "title": "Hardcoded API key placeholder in source",
      "location": "payments/processor.py:13",
      "evidence": "STRIPE_API_KEY = \"REPLACE_WITH_ENV_VAR_NOT_A_REAL_KEY\"",
      "impact": "The pattern guarantees that whoever fills the placeholder will commit a live secret to the repository.",
      "recommendation": "Load from os.environ['STRIPE_API_KEY'] at runtime; fail closed if unset.",
      "references": ["CWE-798", "https://owasp.org/Top10/A02_2021-Cryptographic_Failures/"]
    }
  ]
}
```

See `examples/typical.json` for the full 12-finding output on `processor.py`,
`examples/edge.json` for the 11-finding output on `webhook.py` (covers weak
HMAC + replay + timing-side-channel patterns), and `examples/minimal.json`
which demonstrates the correct empty-list behaviour on a module with no
exploitable surface.

---

## Limitations

- **Single-module scope only.** Multi-module attack chains (e.g. an auth bypass
  in one module exploitable via a payment endpoint in another) require a
  separate orchestrator step that composes findings across modules.
- **Confidence depends on syntactically valid input.** A truncated or
  partially-parseable file produces speculative findings beyond the visible
  code — see `agent-outputs/fallback_notes.txt` for the observed failure
  mode and the JSON-schema + `ast.parse` defences.
- **Coverage limited to OWASP Top 10 categories.** Supply-chain compromise,
  insider threat, and infrastructure-layer vulnerabilities (SSRF that requires
  network access to confirm) are out of scope.
- **Does not validate fixes.** Re-run after each remediation to confirm the
  finding has actually been addressed; do not rely on the previous run's
  output as evidence of resolution.
- **Schema drift risk.** Earlier prompt iterations occasionally produced
  multi-category `owasp_category` values joined by `/`. v1.0.0 explicitly
  forbids this; downstream consumers should still validate with
  `jsonschema` rather than trusting the prompt.

---

## Tests

| Test Run | Input | Expected Output | Actual Output | Pass? |
|---|---|---|---|---|
| 1 — Typical | `payments/processor.py` | ≥ 5 findings including hardcoded-secret + SQL injection (×2) + missing-validation + PII over-fetch + missing-auth | 12 findings (2 critical, 4 high, 3 medium, 2 low, 1 info), severity-ordered, all expected topics present, all anchored to file:line | ✅ |
| 2 — Edge case | `payments/webhook.py` | ≥ 3 findings covering weak HMAC / hardcoded webhook secret / over-logging | 11 findings — surfaces MD5 + non-HMAC construction (A02), hardcoded webhook secret (A07), timing-side-channel comparison (A02), missing replay protection (A04), full charge object logged (A09) | ✅ |
| 3 — Minimal | `notifications/__init__.py` (one comment line) | Empty findings list, summary all zeros, no hallucination | `summary {0,0,0,0,0}`, `findings: []` — zero hallucinated findings | ✅ |

See `examples/{typical,edge,minimal}.json` for the full outputs.

---

## Changelog

### v1.0.0 — 2026-05-03
- Initial release.
- Tested on: 3 OrderFlow modules (`payments/processor.py`, `payments/webhook.py`, `notifications/__init__.py`).
- Tested by: orderflow-engineering.
- Hardening from observed gaps: explicit "exactly ONE owasp_category" rule
  (corrupted-input run produced slash-joined categories — see
  `agent-outputs/fallback_notes.txt`); explicit "empty list is valid"
  rule for files with no exploitable surface (prevents hallucination on
  minimal inputs).
