# Week 2 — The Spec-Driven Feature Factory

A URL shortener service built entirely spec-first using structured YAML prompt templates, formal requirements (SHALL/MUST per RFC 2119), Gherkin scenarios, and full requirement traceability. Every line of implementation code references a REQ-ID, every test traces to a scenario, and a self-critique loop verified security and correctness before submission.

## Tech Stack

Hono · TypeScript · Node.js · Vitest

## Folder Structure

```
week-2/
├── prompts/                        # YAML prompt library (4 templates)
│   ├── spec-writer.yaml            # Generates formal specs from feature requests
│   ├── architect.yaml              # Generates implementation plans from specs
│   ├── code-reviewer.yaml          # Security-focused code review with OWASP scoring
│   └── test-generator.yaml         # Generates test suites from specs
├── specs/                          # Generated specifications
│   ├── url-shortener.yaml          # Formal spec: 7 FRs, 5 NFRs, 10 scenarios, OpenAPI
│   └── diagrams/                   # Mermaid diagrams (sequence, ER, state)
├── src/                            # Hono/TypeScript implementation
│   └── src/                        # Source files with REQ-ID traceability comments
├── tests/                          # Auto-generated vitest suite (23 tests)
├── docs/                           # Documentation and artifacts
│   ├── architect-plan.md
│   ├── self-critique-log.md
│   ├── traceability-matrix.md
│   ├── test-results.txt
│   ├── schema-shortener.json
│   └── schema-validated-output.md
├── REPORT.md                       # 12-question reflection report
└── README.md                       # This file
```

## Setup

```bash
cd week-2/src
npm install
npm test
```

## Report

See [REPORT.md](./REPORT.md) for the full 12-question reflection report with real data, REQ-IDs, and code samples.

---

Part of the [DatariusAI/claude-code-mastery](https://github.com/DatariusAI/claude-code-mastery) 7-week AI engineering portfolio.
