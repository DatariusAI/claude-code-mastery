# Traceability Matrix — URL Shortener Service

| REQ-ID | Description | Code File | Function | Test File | Test Name | Status |
|--------|-------------|-----------|----------|-----------|-----------|--------|
| REQ-SHORT-001 | Shorten valid URL into unique short code | `src/routes/shorten.ts` | `POST /shorten` | `shorten.test.ts` | should return 201 with shortUrl for a valid URL | PASS |
| REQ-SHORT-001 | Generate collision-safe short code | `src/lib/shortener.ts` | `generateCode()` | `shorten.test.ts` | shortCode matches [a-zA-Z0-9]{6} | PASS |
| REQ-SHORT-001 | Store URL record | `src/lib/store.ts` | `save()` | `shorten.test.ts` | should return 201 with shortUrl for a valid URL | PASS |
| REQ-SHORT-002 | Redirect short URL to original | `src/routes/redirect.ts` | `GET /:code` | `redirect.test.ts` | should return 301 redirect for a valid active code | PASS |
| REQ-SHORT-002 | Return 404 for unknown code | `src/routes/redirect.ts` | `GET /:code` | `redirect.test.ts` | should return 404 for a non-existent code | PASS |
| REQ-SHORT-003 | Record analytics on redirect | `src/routes/redirect.ts` | `GET /:code` (analytics recording) | `redirect.test.ts` | should increment click count on successive redirects | PASS |
| REQ-SHORT-003 | Return analytics data | `src/routes/analytics.ts` | `GET /analytics/:code` | `analytics.test.ts` | should return analytics with clickCount, lastAccessedAt, referrers | PASS |
| REQ-SHORT-003 | Click count accuracy | `src/lib/store.ts` | `recordAnalytics()`, `getAnalytics()` | `analytics.test.ts` | should return clickCount = 3 after 3 redirects | PASS |
| REQ-SHORT-004 | Support optional URL expiration | `src/routes/shorten.ts` | `POST /shorten` (expiresAt) | `shorten.test.ts` | should accept and return expiresAt when provided | PASS |
| REQ-SHORT-004 | Expired URL returns 410 | `src/routes/redirect.ts` | `GET /:code` (expiry check) | `redirect.test.ts` | should return 410 for an expired URL | PASS |
| REQ-SHORT-004 | Expired URL returns 410 | `src/routes/redirect.ts` | `GET /:code` (expiry check) | `expiry.test.ts` | should return 410 for an expired URL | PASS |
| REQ-SHORT-004 | No analytics after expiry | `src/routes/redirect.ts` | `GET /:code` (expiry guard) | `expiry.test.ts` | should not record analytics for expired URL access | PASS |
| REQ-SHORT-004 | No-expiry URL always active | `src/routes/redirect.ts` | `GET /:code` | `expiry.test.ts` | should redirect indefinitely when no expiresAt is set | PASS |
| REQ-SHORT-005 | Validate URL format and scheme | `src/lib/validator.ts` | `validateUrl()` | `validator.test.ts` | should accept valid https/http URL | PASS |
| REQ-SHORT-005 | Reject invalid URLs | `src/lib/validator.ts` | `validateUrl()` | `validator.test.ts` | should reject URL without protocol | PASS |
| REQ-SHORT-005 | Reject URLs exceeding max length | `src/lib/validator.ts` | `validateUrl()` | `validator.test.ts` | should reject URL exceeding 2048 characters | PASS |
| REQ-SHORT-005 | Reject blocked domains | `src/lib/validator.ts` | `validateUrl()` | `validator.test.ts` | should reject a blocked domain | PASS |
| REQ-SHORT-005 | Reject duplicate URLs (409) | `src/routes/shorten.ts` | `POST /shorten` | `shorten.test.ts` | should return 409 for a duplicate URL | PASS |
| REQ-SHORT-005 | Blocked domain returns 403 | `src/routes/shorten.ts` | `POST /shorten` | `shorten.test.ts` | should return 403 for a blocked domain | PASS |
| REQ-SHORT-006 | Delete short URL | `src/routes/delete.ts` | `DELETE /:code` | — | (not directly tested) | PARTIAL |
| REQ-SHORT-007 | Consistent error response shape | `src/routes/*.ts` | All error returns | `shorten.test.ts` | error.code present on 400/403/409 responses | PASS |
| REQ-SHORT-007 | Global error handler | `src/index.ts` | `app.onError()` | — | (covered implicitly) | PASS |

---

## Summary

- **Total requirements:** 7 (REQ-SHORT-001 through REQ-SHORT-007)
- **Fully covered:** 6 (REQ-SHORT-001, 002, 003, 004, 005, 007)
- **Partially covered:** 1 (REQ-SHORT-006 — DELETE endpoint implemented but no dedicated test for DELETE + subsequent 410)
- **Not covered:** 0
