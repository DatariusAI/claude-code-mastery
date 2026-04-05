# Schema-Validated Output — shortener.ts

**Prompt:** "Respond ONLY in JSON matching this schema. No prose, no markdown fences."

**Schema:** `week-2/docs/schema-shortener.json`

**Raw JSON response:**

```json
{
  "function_name": "generateCode",
  "req_ids": ["REQ-SHORT-001"],
  "typescript_code": "import { CODE_LENGTH, CODE_CHARS, MAX_CODE_RETRIES } from '../constants.js';\nimport { findByCode } from './store.js';\nimport { randomBytes } from 'node:crypto';\n\nexport function generateCode(): string {\n  for (let attempt = 0; attempt < MAX_CODE_RETRIES; attempt++) {\n    const bytes = randomBytes(CODE_LENGTH);\n    let code = '';\n    for (let i = 0; i < CODE_LENGTH; i++) {\n      code += CODE_CHARS[bytes[i] % CODE_CHARS.length];\n    }\n    if (!findByCode(code)) {\n      return code;\n    }\n  }\n  throw new Error(`Failed to generate unique code after ${MAX_CODE_RETRIES} attempts`);\n}",
  "error_cases": [
    {
      "condition": "All generated codes collide with existing entries after MAX_CODE_RETRIES attempts",
      "error_code": "CODE_GENERATION_FAILED",
      "http_status": 500
    }
  ]
}
```

**Validation result:** Passes schema validation — all required fields present, correct types.
