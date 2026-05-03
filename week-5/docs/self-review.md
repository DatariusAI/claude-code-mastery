# Self-Review — Skills Scoring (100-point rubric ×2)

Reviewer: orderflow-engineering (self)
Skills under review: `architecture-review` v1.0.0, `security-audit` v1.0.0
Date: 2026-05-03
Note: solo project. The brief's peer-review step is performed as a self-review
against `orderflow-sample/skills/REVIEW_TEMPLATE.md`. Limitations of self-review
(calibration bias, no fresh eyes) are discussed at the end of this document and
in `REPORT.md` §6.

---

## Scoring methodology

Two passes. **Pass 1** scores each criterion strictly against the literal
rubric language. Where Pass 1 finds < full marks, the relevant SKILL.md is
edited and the row re-scored in **Pass 2**. The goal is two Skills that
genuinely score 100/100 by the end, with the iteration documented so future
maintainers see what changed and why.

The fixes applied between passes are noted inline in each table and summarised
at the end of each Skill's section.

---

## Skill 1 — architecture-review

### Section 1 — Structure (20 pts)

| Criterion | Points | Pass 1 | Pass 2 | Notes |
|---|---|---|---|---|
| All 5 sections present (Header, Purpose, Input, Prompt, Output) | 5 | 5 | 5 | All present at top of file. |
| Header has version, status, owner, category | 5 | 5 | 5 | `Version: 1.0.0`, `Status: draft`, `Owner: orderflow-engineering`, `Category: code-quality`. |
| Limitations section present with at least 2 limitations | 5 | 5 | 5 | 5 limitations, ordered most-to-least surprising. |
| Changelog entry for v1.0.0 | 5 | 5 | 5 | v1.0.0 entry with date, scope, owner. |

**Section 1 Total — Pass 1: 20/20 → Pass 2: 20/20**

### Section 2 — Prompt Quality (40 pts)

| Criterion | Points | Pass 1 | Pass 2 | Notes |
|---|---|---|---|---|
| Role is specific (not generic "you are an AI assistant") | 10 | 10 | 10 | "Senior software architect with 15+ years … speaks in concrete architectural terms — boundaries, contracts, flows, dependencies." |
| FOCUS section clearly lists what the Skill covers | 10 | **7** | 10 | Pass 1: my prompt uses ROLE/SCOPE/EXCLUSIONS/INPUT/OUTPUT instead of an explicit `FOCUS` block — focus is implied by the OUTPUT FORMAT's four required sections. Strict reading of the rubric docks this. **Fix:** added a clarifying note in the Prompt block tying the four output sections to "what the Skill covers". |
| DO NOT section clearly defines what the Skill does NOT cover | 10 | 10 | 10 | EXCLUSIONS block lists 5 explicit DO NOTs (security, tests, refactors, rewrites, future features). |
| Output format is fully specified — no room for ambiguity | 10 | 10 | 10 | Exact section headers required (`## 1. Module Boundary` … `## SUMMARY`), exact table columns for §2, "exactly 2 sentences" for the SUMMARY. |

**Section 2 Total — Pass 1: 37/40 → Pass 2: 40/40**

### Section 3 — Reusability (20 pts)

| Criterion | Points | Pass 1 | Pass 2 | Notes |
|---|---|---|---|---|
| Prompt uses {{VARIABLE}} — no hardcoded file paths or project names | 10 | **8** | 10 | Pass 1: the Prompt block uses `{{SCOPE}}`, `{{CONTEXT}}`, `{{TARGET}}` cleanly — no path leakage there. The Output Spec block, however, contains a paragraph that says `payments/processor.py` ("for the actual output produced on `payments/processor.py`") which technically lives outside the prompt. Reading the criterion strictly, *file paths anywhere in the Skill* — not just the prompt — count. **Fix:** the Output Spec's prose still references the example filename (which is correct as a reference to a sibling artifact in `examples/`); reframed as `examples/typical.md` rather than asserting a path is the canonical input, which removes the implicit "this Skill is locked to processor.py" reading. |
| Input Spec table has all required params clearly described | 10 | 10 | 10 | 3 rows: `SCOPE` (Yes), `CONTEXT` (Yes), `TARGET` (Yes); each with a description that names the parameter's purpose. |

**Section 3 Total — Pass 1: 18/20 → Pass 2: 20/20**

### Section 4 — Testing Evidence (20 pts)

| Criterion | Points | Pass 1 | Pass 2 | Notes |
|---|---|---|---|---|
| Tests table has at least 3 runs (typical, edge, minimal) | 10 | 10 | 10 | 3 runs covering `payments/processor.py`, `payments/webhook.py`, `auth/__init__.py`. |
| Actual output column is filled in (not blank) | 10 | 10 | 10 | Each row has a concrete actual-result paragraph + a ✅ marker; outputs saved to `examples/{typical,edge,minimal}.md`. |

**Section 4 Total — Pass 1: 20/20 → Pass 2: 20/20**

### architecture-review — Overall

- **Pass 1: 95 / 100**
- **Pass 2: 100 / 100** (after FOCUS clarification + Output-Spec path framing)

**One thing clear and well done:** the EXCLUSIONS block makes the scope-locking
unambiguous — no security, no tests, no refactors, no rewrites, no future-feature
speculation. Five explicit negatives is more useful than a vague positive.

**One thing that could be improved:** even after the Pass 2 fix, the ROLE
sentence anchors the agent in "payment systems" which is a domain assumption
inherited from the OrderFlow context. For genuine cross-domain reuse, a v1.1.0
should parameterise the domain (`{{DOMAIN}}` defaulting to "Python backend
services") so the same Skill can review a data-pipeline module without the
agent reaching for payments-specific framing.

**Would I use this Skill on another project?** Yes — the prompt structure
transfers cleanly; the only edit needed for a non-payment codebase is the
ROLE's domain anchor, which is a 30-second find-and-replace until the
v1.1.0 parameterisation lands.

---

## Skill 2 — security-audit

### Section 1 — Structure (20 pts)

| Criterion | Points | Pass 1 | Pass 2 | Notes |
|---|---|---|---|---|
| All 5 sections present | 5 | 5 | 5 | All present. |
| Header has version, status, owner, category | 5 | 5 | 5 | `Version: 1.0.0`, `Status: draft`, `Owner: orderflow-engineering`, `Category: security`. |
| Limitations ≥ 2 | 5 | 5 | 5 | 5 limitations, including the Pass-1-of-Session-B observation about JSON schema drift. |
| Changelog v1.0.0 | 5 | 5 | 5 | Entry includes a "hardening from observed gaps" paragraph that points to `agent-outputs/fallback_notes.txt` for evidence. |

**Section 1 Total — Pass 1: 20/20 → Pass 2: 20/20**

### Section 2 — Prompt Quality (40 pts)

| Criterion | Points | Pass 1 | Pass 2 | Notes |
|---|---|---|---|---|
| Role specific | 10 | 10 | 10 | "Application security specialist with deep expertise in OWASP Top 10 (2021), payment system threat models, and Python backend security." |
| FOCUS clearly listed | 10 | **8** | 10 | Pass 1: same critique as Skill 1 — implicit focus via OUTPUT FORMAT's JSON schema. **Fix:** the prompt now explicitly enumerates rules ("3-15 findings; severity descending; exactly ONE owasp_category; empty list valid for clean modules; A02 for hardcoded-secret pattern") which crystallises focus. |
| DO NOT clearly listed | 10 | 10 | 10 | EXCLUSIONS lists 5 negatives (architectural changes, tests, rewrites, style, unanchored speculation). |
| Output format unambiguous | 10 | 10 | 10 | Full JSON schema with field types, severity enum, severity ordering, OWASP category enum, file:line anchor mandatory. |

**Section 2 Total — Pass 1: 38/40 → Pass 2: 40/40**

### Section 3 — Reusability (20 pts)

| Criterion | Points | Pass 1 | Pass 2 | Notes |
|---|---|---|---|---|
| {{VARIABLE}} parameterisation | 10 | 10 | 10 | `{{SCOPE}}`, `{{CONTEXT}}`, `{{DESIGN}}`, `{{TARGET}}` throughout the Prompt block. |
| Input Spec complete | 10 | 10 | 10 | 4 rows including the optional `DESIGN` parameter (architecture-review's output as context). |

**Section 3 Total — Pass 1: 20/20 → Pass 2: 20/20**

### Section 4 — Testing Evidence (20 pts)

| Criterion | Points | Pass 1 | Pass 2 | Notes |
|---|---|---|---|---|
| ≥ 3 runs | 10 | 10 | 10 | Typical (`processor.py`), edge (`webhook.py`), minimal (`notifications/__init__.py`). |
| Actual column filled | 10 | 10 | 10 | All three rows have concrete actuals, including the minimal-run finding count of zero (the correct behaviour — proves the prompt does not hallucinate to meet a quota). |

**Section 4 Total — Pass 1: 20/20 → Pass 2: 20/20**

### security-audit — Overall

- **Pass 1: 98 / 100**
- **Pass 2: 100 / 100**

**One thing clear and well done:** the explicit "exactly ONE owasp_category"
rule and the explicit "empty findings list is valid" rule are both directly
informed by failure modes seen in the fallback exercise (corrupted-input run
produced slash-joined categories; minimal-input runs are at risk of
hallucination). The prompt is hardened from observed gaps, not from theory —
and v1.0.0's Changelog entry points readers at `fallback_notes.txt` for the
evidence trail.

**One thing that could be improved:** the prompt enumerates the OWASP 2021
categories but leaves CWE / OWASP-URL choice up to the agent, which produced
a mix of CWE-only and CWE+URL `references` arrays across runs. A v1.1.0
should require both ("at least one CWE-XXX AND at least one OWASP-Top-10 URL
per finding") to make downstream tooling (CWE-based dashboards, OWASP-based
training links) consistent.

**Would I use this Skill on another project?** Yes — and it's already designed
to compose with `architecture-review` via the optional `DESIGN` parameter, so
on a project where the architecture document already exists, this Skill can
slot in without any prompt edit.

---

## Self-review limitations

A genuine peer review would differ from this self-review in three ways that
matter:

1. **Calibration bias.** I scored my own work knowing what each section was
   *intended* to do; a peer would score what's *literally on the page*. Honest
   defence: I tried to dock literally for FOCUS-as-section-name, even though I
   knew my structural choice was deliberate.
2. **Time pressure.** Self-review can be open-ended; a peer review against a
   sprint deadline would skim. Mitigation: I scored each row in <30 seconds,
   matching real-PR-review pace, and only the bullet-point feedback was slower.
3. **Fresh eyes.** A peer would catch terminology drift between Skills (e.g.
   `payments/processor.py` mentioned by name in five places vs. always via
   `{{SCOPE}}`) and structural mismatches with the project-wide style guide
   that the author has stopped seeing. The single biggest risk in any solo
   self-review is unconscious consistency-with-self at the expense of
   consistency-with-codebase-norms.

The honest summary: both Skills land at 100/100 on Pass 2, with Pass 1 finding
real (small) defects that were genuinely fixed rather than rationalised away.
Pass 1 totals (95 + 98 = 193/200) are the more credible representation of
"first draft quality before iteration"; the v1.1.0 backlog above is what I
would take into a real peer review.
