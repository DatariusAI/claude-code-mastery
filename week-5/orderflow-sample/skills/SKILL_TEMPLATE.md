# Skill: [YOUR SKILL NAME HERE]
# Version: 1.0.0
# Status: draft
# Owner: [your-name / your-team]
# Category: [code-quality | security | testing | documentation | deployment]
# Created: [date]

---

## Purpose

[One paragraph: What does this Skill do? When should an engineer use it?
What problem does it solve? What does it produce?]

---

## Input

| Parameter | Required | Description |
|---|---|---|
| `SCOPE` | Yes | Module or file path to analyse (e.g. `payments/processor.py`) |
| `CONTEXT` | Yes | CLAUDE.md project context |
| `[PARAM_2]` | No | [Description of optional param] |

---

## Prompt

```
You are a [ROLE — e.g. senior software architect / QA engineer / security specialist].

Your job is to [ONE CLEAR RESPONSIBILITY].

SCOPE: {{SCOPE}} only.

FOCUS ONLY ON:
- [specific concern 1]
- [specific concern 2]
- [specific concern 3]

DO NOT:
- [thing that another Skill handles]
- [thing outside your role]
- [thing that would cause scope creep]

You will receive: CLAUDE.md project context + [list what else you receive].
Use these as your source of truth. Do not make up information not present in the inputs.

OUTPUT FORMAT:
[Specify exact format — JSON array / markdown sections / code file]
Required sections / fields:
- [field 1]: [description]
- [field 2]: [description]
- [field 3]: [description]

No preamble. No explanation outside the specified format.
```

---

## Output Spec

```
[Paste an example of what the output looks like — a real sample with fake data]

Example:
## MUST_FIX
1. [file:line] — [issue description]. Fix: [recommended fix].

## SHOULD_FIX
2. [file:line] — [issue description].

## NICE_TO_HAVE
3. [file:line] — [issue description].

## SUMMARY
[2 sentences max. What did the Skill find overall?]
```

---

## Limitations

- This Skill does NOT cover [adjacent concern — e.g. security, testing, performance]
- Results may be incomplete on files longer than ~500 lines — chunk and re-run
- [Any other known limitation you discovered during testing]

---

## Tests

| Test Run | Input | Expected Output | Actual Output | Pass? |
|---|---|---|---|---|
| 1 — Typical | `payments/processor.py` | [describe expected] | [describe actual] | ✅ / ❌ |
| 2 — Edge case | [edge case input] | [describe expected] | [describe actual] | ✅ / ❌ |
| 3 — Minimal | [empty/minimal input] | [describe expected] | [describe actual] | ✅ / ❌ |

---

## Changelog

### v1.0.0 — [date]
- Initial release
- Tested on: OrderFlow sample repo (payments/processor.py)
- Tested by: [your name]
