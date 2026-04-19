# Bug Audit — Hono Source Code Review

Findings from AI-assisted source code analysis of honojs/hono v4.12.9.

| # | Severity | File | Finding | Status |
|---|----------|------|---------|--------|
| 1 | MEDIUM | `src/compose.ts:53` | Error handling only catches `Error` instances. Non-Error throws (strings, objects, `undefined`) bypass `onError` and propagate uncaught. This is intentional but undocumented — middleware authors may not expect it. | By Design |
| 2 | LOW | `src/compose.ts:34` | `next()` called multiple times throws a generic `Error` with no context about which middleware caused the violation. Debugging is harder without the middleware name or index. | Confirmed |
| 3 | MEDIUM | `src/router/smart-router/` | SmartRouter silently swallows `UnsupportedPathError` from RegExpRouter and falls back to TrieRouter. If all routers fail, the error from the last router is thrown — potentially masking the real issue. | By Design |
| 4 | LOW | `src/hono-base.ts` | Default `errorHandler` logs to `console.error` and returns plain text "Internal Server Error". In production, this leaks no details (good) but provides no request ID or correlation for debugging. | Enhancement |
| 5 | HIGH | `src/utils/jwt/` | JWT utility implements cryptographic operations from scratch using Web Crypto API. While correct, any custom crypto implementation carries higher risk than using established libraries. Requires careful review on updates. | Risk |
| 6 | MEDIUM | `src/middleware/jwt/` | JWT middleware relies on the internal `src/utils/jwt/` implementation. Token validation edge cases (clock skew, algorithm confusion) depend entirely on the custom implementation's correctness. | Risk |
| 7 | LOW | `~/package.json` | Home directory `package.json` contained two concatenated JSON objects (malformed). This broke all `npm install` and `npx` commands system-wide. Fixed during this session. | Fixed |
| 8 | LOW | `.gitignore` | Originally only contained `node_modules/`. Missing entries for `.env`, `.env.*`, `dist/`, `.claude/`, `*.log`. Fixed during this session. | Fixed |
