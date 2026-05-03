# Skills Library — Reference

This is the reference doc for `orderflow-sample/skills/` — the library of
reusable agent prompts built during Week 5.

## Why a Skills library exists

Per the Session 10 framing: a Skill is the unit of *reuse* for prompts.
A prompt run once on one file is a script; a prompt parameterised,
versioned, tested, and stored alongside its example outputs is a Skill
that survives the project. The library is the place where Skills are
indexed, discovered, and versioned.

Four properties separate a Skill from a one-off prompt:

1. **Parameterised.** `{{SCOPE}}` not `payments/processor.py`. Reusable
   across modules and projects.
2. **Versioned.** Semver from v1.0.0 onward. Backwards-compatible
   prompt edits go to v1.x.0; breaking output schema changes go to
   v2.0.0.
3. **Tested.** A 3-row Tests table covering typical / edge / minimal
   inputs, with actual outputs saved to `examples/`.
4. **Bounded.** Limitations section is first-class — what the Skill
   does *not* do is as important as what it does.

## The 5-part Skill structure

Every SKILL.md has these five parts in order:

| Part | Purpose | Common mistake |
|---|---|---|
| **Header** (Name, Version, Status, Owner, Category, Created) | Single line of metadata for discovery | Missing `Owner`, or `Status: TBD` (use `draft` / `stable` / `deprecated`) |
| **Purpose** | One paragraph: what + when + output | Vague "this Skill helps with X" instead of concrete what / when / output |
| **Input Spec** | Parameter table with required / optional / description | Listing `{{VARIABLE}}` without saying what kind of value it expects |
| **Prompt Body** | The parameterised prompt, in a fenced code block | Hardcoded paths inside the prompt; no `{{VARIABLE}}` substitution |
| **Output Spec** | Concrete example with fake data | Showing the shape but not a realistic example, or pasting a real run with project-specific paths |

Plus three required extra sections:

- **Limitations** — at least 2, ideally 3-5. The most useful ones are
  the surprising ones (e.g. "single-module scope only — multi-module
  attack chains require a separate orchestrator").
- **Tests** — 3 rows minimum: typical, edge, minimal. The minimal-input
  row is the most diagnostic — it proves the Skill knows when to
  return nothing.
- **Changelog** — semver entries with date, scope, owner, and (for
  later versions) "Hardening from observed gaps" notes that explain
  what real failure mode prompted the version bump.

## How to add a new Skill

1. Copy `SKILL_TEMPLATE.md` to `skills/your-skill-name/SKILL.md`.
2. Fill in all 5 sections + Limitations + Tests + Changelog.
3. Run 3 test cases (typical, edge, minimal) and save the actual outputs
   to `skills/your-skill-name/examples/`.
4. Update the Skill Index table in `skills/README.md` with a row
   linking to the new SKILL.md.
5. (If working with a partner) ask for review using
   `REVIEW_TEMPLATE.md`. (If solo) self-review honestly — see
   `docs/self-review.md` for the two-pass pattern.

## Parameterisation vs. string-formatting

The `{{VARIABLE}}` placeholders are **template markers for the prompt
author**, not Python format strings. The intended usage is:

- The Skill author writes `{{SCOPE}}` in the prompt body.
- A human (or an Orchestrator) substitutes the literal value at the
  moment of invocation: e.g. replace every `{{SCOPE}}` with
  `payments/processor.py` before pasting the prompt into a Claude
  session.
- The Skill is **not** auto-substituted by tooling in v1.0.0.

This is deliberate. A real `format()`-based templating layer would add
a runtime dependency that makes the Skill harder to copy-paste into a
fresh Claude session. v1.0.0 keeps Skills as pure-markdown artifacts
that work with zero infrastructure.

## Discoverability — the Skill Index

`skills/README.md` has a table:

| Skill | Category | Version | Status | Owner |
|---|---|---|---|---|
| [architecture-review](./architecture-review/SKILL.md) | code-quality | 1.0.0 | draft | orderflow-engineering |
| [security-audit](./security-audit/SKILL.md) | security | 1.0.0 | draft | orderflow-engineering |

This is the single source of truth for "what Skills exist and where
to find them". When you add a Skill, update this table. When you
deprecate a Skill, change the Status column to `deprecated` rather
than removing the row — historical references in PR descriptions need
the link to keep working.

## Versioning

Semver applies to the prompt + the output schema:

| Change | Bump |
|---|---|
| Typo fix in prompt prose | none (in-place, no version bump) |
| Adding a Limitation entry | none (Limitations are observation, not contract) |
| Adding an optional `{{PARAMETER}}` | minor (v1.0.0 → v1.1.0) — old callers still work |
| Tightening a prompt rule (e.g. "exactly ONE owasp_category") | minor — old outputs that violated the rule were always wrong |
| Adding a required output field | **major** (v1.x → v2.0.0) — breaks downstream parsers |
| Changing severity enum values | **major** — breaks downstream filters |
| Renaming a section header | **major** — breaks anything that greps for the header |

Every version bump gets a Changelog entry with date, what changed, and
a short "why" — ideally pointing to the failure mode that motivated
the change (see `security-audit` v1.0.0's "Hardening from observed
gaps" section, which references `agent-outputs/fallback_notes.txt`).
