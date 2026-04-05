# Implementation Plan — URL Shortener Service

**Spec:** `week-2/specs/url-shortener.yaml`
**Tech Stack:** Hono + TypeScript + Node.js adapter + in-memory Map store

---

## Component List

| # | Component | File Path | Responsibility | REQ-IDs |
|---|-----------|-----------|----------------|---------|
| 1 | Constants | `src/constants.ts` | Central config: base URL, code length, max URL length, blocked domains | REQ-SHORT-005, NFR-004 |
| 2 | Types | `src/types.ts` | TypeScript interfaces for all data models and API shapes | REQ-SHORT-001 through 007 |
| 3 | Store | `src/lib/store.ts` | In-memory Map-based data store for URLs and analytics | REQ-SHORT-001, 003, 004, 005, 006 |
| 4 | Shortener | `src/lib/shortener.ts` | Short code generation (6-char, collision-safe) | REQ-SHORT-001 |
| 5 | Validator | `src/lib/validator.ts` | URL validation: format, length, scheme, blocklist | REQ-SHORT-005, NFR-004 |
| 6 | Shorten Route | `src/routes/shorten.ts` | POST /shorten endpoint | REQ-SHORT-001, 003, 005, 007 |
| 7 | Redirect Route | `src/routes/redirect.ts` | GET /:code endpoint with analytics recording | REQ-SHORT-002, 003, 004, 007 |
| 8 | Analytics Route | `src/routes/analytics.ts` | GET /analytics/:code endpoint | REQ-SHORT-003, 007 |
| 9 | Delete Route | `src/routes/delete.ts` | DELETE /:code endpoint | REQ-SHORT-006, 007 |
| 10 | Entry Point | `src/index.ts` | Hono app setup, route registration, error handler | REQ-SHORT-001 through 007, NFR-005 |

---

## TypeScript Interfaces

```typescript
// UrlRecord — stored in the URL map
interface UrlRecord {
  id: string;                  // UUID
  originalUrl: string;         // validated original URL
  shortCode: string;           // 6-char alphanumeric
  createdAt: string;           // ISO 8601
  expiresAt: string | null;    // ISO 8601 or null
  isActive: boolean;           // false if deleted
}

// AnalyticsEvent — stored per redirect
interface AnalyticsEvent {
  id: string;                  // UUID
  urlId: string;               // references UrlRecord.id
  accessedAt: string;          // ISO 8601
  referrer: string;            // HTTP Referer header or empty string
  ipHash: string;              // SHA-256 of client IP
}

// ShortenRequest — POST /shorten body
interface ShortenRequest {
  url: string;                 // required, max 2048 chars
  expiresAt?: string;          // optional ISO 8601, must be in future
}

// ShortenResponse — 201 response body
interface ShortenResponse {
  shortUrl: string;            // full short URL
  originalUrl: string;         // echoed back
  shortCode: string;           // the generated code
  createdAt: string;           // ISO 8601
  expiresAt: string | null;    // null if no expiry
}

// AnalyticsResponse — GET /analytics/:code response body
interface AnalyticsResponse {
  shortCode: string;
  originalUrl: string;
  clickCount: number;
  lastAccessedAt: string | null;
  referrers: string[];
}

// ErrorResponse — standard error envelope (REQ-SHORT-007)
interface ErrorResponse {
  error: {
    code: number;              // HTTP status code
    message: string;           // human-readable
    details: string | null;    // optional context
  };
}
```

---

## Implementation Tasks

### Task 1 — Set up constants and types
- **REQ-IDs:** REQ-SHORT-005, NFR-004
- **Files:** `src/constants.ts`, `src/types.ts`
- **Acceptance criteria:**
  - All interfaces compile with `tsc --noEmit`
  - Constants are exported and used by all downstream modules
- **Risk flags:** None — pure type definitions

### Task 2 — Implement in-memory store
- **REQ-IDs:** REQ-SHORT-001, REQ-SHORT-003, REQ-SHORT-004, REQ-SHORT-005, REQ-SHORT-006
- **Files:** `src/lib/store.ts`
- **Acceptance criteria:**
  - `save()` stores a UrlRecord and returns it
  - `findByCode()` returns UrlRecord or undefined
  - `findByOriginal()` returns UrlRecord or undefined (for duplicate check)
  - `recordAnalytics()` appends an event
  - `getAnalytics()` returns all events for a code
  - `deleteByCode()` sets `isActive = false`
- **Risk flags:**
  - Memory growth: no eviction strategy. Acceptable for demo/portfolio scope.
  - Not thread-safe in clustered Node.js — acceptable for single-process demo.

### Task 3 — Implement short code generator
- **REQ-IDs:** REQ-SHORT-001
- **Files:** `src/lib/shortener.ts`
- **Acceptance criteria:**
  - Returns 6-char alphanumeric string
  - Checks store for collisions before returning
  - Max 10 retries on collision, then throws
- **Risk flags:**
  - Collision probability increases with dataset size. 62^6 = ~56 billion combinations — safe for demo scale.

### Task 4 — Implement URL validator
- **REQ-IDs:** REQ-SHORT-005, NFR-004
- **Files:** `src/lib/validator.ts`
- **Acceptance criteria:**
  - Rejects non-http/https schemes
  - Rejects URLs > 2048 chars
  - Rejects malformed URLs (try/catch on `new URL()`)
  - Rejects blocked domains
  - Returns `{ valid: true }` or `{ valid: false, reason: string }`
- **Risk flags:**
  - URL constructor differences across runtimes — use standard `new URL()` which Hono/Node.js supports.

### Task 5 — Implement POST /shorten route
- **REQ-IDs:** REQ-SHORT-001, REQ-SHORT-005, REQ-SHORT-007
- **Files:** `src/routes/shorten.ts`
- **Acceptance criteria:**
  - Validates input via validator
  - Checks for duplicate via store.findByOriginal()
  - Generates code, stores record, returns 201
  - All error paths use ErrorResponse format
  - expiresAt validated as future ISO 8601 datetime
- **Risk flags:**
  - Missing body parsing error handling — Hono's `c.req.json()` can throw on malformed JSON.
  - OWASP: validate `url` field type (must be string, not array or object).

### Task 6 — Implement GET /:code redirect route
- **REQ-IDs:** REQ-SHORT-002, REQ-SHORT-003, REQ-SHORT-004, REQ-SHORT-007
- **Files:** `src/routes/redirect.ts`
- **Acceptance criteria:**
  - Lookup by code, return 404 if not found
  - Check `isActive`, return 410 if deleted
  - Check `expiresAt`, return 410 if expired
  - Record analytics event with hashed IP
  - Return 301 with Location header
- **Risk flags:**
  - IP hashing: must use crypto.subtle or Node.js crypto — not a custom hash.
  - Referrer header may be absent — default to empty string.

### Task 7 — Implement GET /analytics/:code route
- **REQ-IDs:** REQ-SHORT-003, REQ-SHORT-007
- **Files:** `src/routes/analytics.ts`
- **Acceptance criteria:**
  - Lookup by code, return 404 if not found
  - Return clickCount, lastAccessedAt, unique referrers
  - Works for expired and deleted URLs (analytics preserved)
- **Risk flags:** None — read-only endpoint.

### Task 8 — Implement DELETE /:code route
- **REQ-IDs:** REQ-SHORT-006, REQ-SHORT-007
- **Files:** `src/routes/delete.ts`
- **Acceptance criteria:**
  - Lookup by code, return 404 if not found
  - Set `isActive = false`, return 204
  - Analytics data preserved after deletion
- **Risk flags:** None — simple state transition.

### Task 9 — Wire up entry point and global error handler
- **REQ-IDs:** REQ-SHORT-007, NFR-005
- **Files:** `src/index.ts`
- **Acceptance criteria:**
  - All 4 route modules registered
  - Global `onError` handler returns ErrorResponse format
  - No stack traces in production error responses
  - Server starts on configurable PORT
- **Risk flags:**
  - Route order matters: `GET /:code` is a wildcard — must be registered after `/shorten` and `/analytics/:code`.
