# Self-Critique Log

## Cycle 1 — src/routes/shorten.ts

### File reviewed
`week-2/src/src/routes/shorten.ts` (original version, pre-fix)

### Review findings

```json
{
  "owasp_findings": [
    {
      "category": "A04:2021 - Insecure Design",
      "description": "Blocked domains return HTTP 400 instead of HTTP 403 as required by spec (SCEN-004 variant). The validator returns blocked=true but the route does not differentiate.",
      "severity": 4,
      "line_reference": "lines 38-43",
      "fix": "Check validation.blocked flag and return 403 for blocklisted domains"
    },
    {
      "category": "A03:2021 - Injection",
      "description": "No Content-Type validation. Endpoint accepts any Content-Type header, which could lead to unexpected parsing behavior.",
      "severity": 3,
      "line_reference": "line 19",
      "fix": "Validate Content-Type is application/json before parsing body"
    }
  ],
  "spec_compliance": [
    { "req_id": "REQ-SHORT-001", "status": "FULL", "notes": "Generates code, stores record, returns 201 with all required fields" },
    { "req_id": "REQ-SHORT-005", "status": "PARTIAL", "notes": "Validation works but blocked domains return 400 instead of spec-required 403" },
    { "req_id": "REQ-SHORT-007", "status": "FULL", "notes": "All error paths use consistent ErrorResponse envelope" }
  ],
  "bug_risks": [
    {
      "description": "expiresAt field not type-checked — if a number or object is passed, new Date() silently accepts it",
      "location": "line 57",
      "severity": 5
    },
    {
      "description": "generateCode() can throw on collision exhaustion — uncaught exception would produce unstructured 500",
      "location": "line 72",
      "severity": 6
    }
  ],
  "required_fixes": [
    "Differentiate blocked domain (403) from invalid URL (400) in route handler",
    "Add Content-Type validation before JSON parsing",
    "Type-check expiresAt as string before Date parsing",
    "Wrap generateCode() in try/catch to return structured error"
  ],
  "score": {
    "security": 6,
    "correctness": 7
  }
}
```

### Required fixes applied
- Added Content-Type check: returns 400 if not `application/json`
- Updated validator to return `blocked: true` flag for blocklisted domains
- Route now returns 403 for blocked domains, 400 for other validation failures
- Added `typeof body.expiresAt !== 'string'` check before Date parsing
- Wrapped `generateCode()` in try/catch, returns structured 500 on failure
- Added REQ-SHORT-004 to file header (expiresAt validation is part of this route)

### Score after cycle 1
security: 6/10 | correctness: 7/10

---

## Cycle 2 — src/routes/shorten.ts (after fixes)

### File reviewed
`week-2/src/src/routes/shorten.ts` (post-fix version)

### Review findings

```json
{
  "owasp_findings": [],
  "spec_compliance": [
    { "req_id": "REQ-SHORT-001", "status": "FULL", "notes": "Code generation, storage, and 201 response all correct" },
    { "req_id": "REQ-SHORT-004", "status": "FULL", "notes": "expiresAt validated as string, ISO 8601, and future date" },
    { "req_id": "REQ-SHORT-005", "status": "FULL", "notes": "URL validation complete — format, length, scheme, blocklist (403), duplicate (409)" },
    { "req_id": "REQ-SHORT-007", "status": "FULL", "notes": "All error paths use ErrorResponse envelope with code, message, details" }
  ],
  "bug_risks": [],
  "required_fixes": [],
  "score": {
    "security": 9,
    "correctness": 9
  }
}
```

### Required fixes applied
None — `required_fixes` array is empty. Stopping cycle.

### Score after cycle 2
security: 9/10 | correctness: 9/10

---

**Self-critique loop complete.** Stopped after 2 cycles — zero required fixes remaining.
