# CLAUDE.md

## Project Overview

Hono ("flame" in Japanese) is a small, ultrafast web framework built entirely on Web Standards. It runs on Cloudflare Workers, Fastly Compute, Deno, Bun, Vercel, AWS Lambda, Lambda@Edge, and Node.js. It has zero production dependencies — everything is implemented from scratch using only the Web Standard API (Request, Response, fetch, etc.).

## Tech Stack

- **Language:** TypeScript (strict mode, target ES2022)
- **Module system:** ES modules (`"type": "module"` in package.json)
- **Package manager:** Bun (bun@1.2.20)
- **Build tool:** esbuild, custom build script at `build/build.ts`
- **Test framework:** Vitest (with globals enabled), plus runtime-specific test suites for Deno (`deno test`) and Bun (`bun test`)
- **Linting:** ESLint via `@hono/eslint-config`
- **Formatting:** Prettier (no semicolons, single quotes, 100 char width, trailing commas ES5)
- **CI:** GitHub Actions — tests across Node.js 18/20/22, Deno, Bun, Cloudflare workerd, Fastly, Lambda, Lambda@Edge
- **Coverage:** V8 provider via `@vitest/coverage-v8`, uploaded to Codecov
- **Engines:** Node.js >= 16.9.0

## Architecture

The codebase follows a layered architecture with clear dependency boundaries (no circular imports):

```
Layer 1 (bottom):  src/utils/*          — standalone utility functions
Layer 2:           src/router/*         — five router implementations
Layer 3:           src/context.ts       — Context, HonoRequest, core types
                   src/types.ts
                   src/request.ts
Layer 4:           src/compose.ts       — koa-compose-style middleware pipeline
                   src/hono-base.ts     — HonoBase class (core framework logic)
Layer 5:           src/helper/*         — feature modules (cookie, html, ssg, streaming, etc.)
Layer 6:           src/middleware/*      — 26 middleware modules
Layer 7:           src/adapter/*        — 9 platform adapters
Layer 8:           src/client/*         — typed RPC client
Isolated:          src/jsx/*            — full JSX/DOM rendering engine (largely self-contained)
```

**Router strategy:** The default `Hono` class (src/hono.ts) uses `SmartRouter`, which wraps `RegExpRouter` and `TrieRouter` — it tries the fast RegExpRouter first and falls back to TrieRouter for patterns RegExpRouter can't handle. Two presets offer alternatives:
- `hono/tiny` — uses `PatternRouter` (smallest bundle)
- `hono/quick` — uses `SmartRouter` with `LinearRouter` + `TrieRouter`

**Middleware pipeline:** `src/compose.ts` implements koa-compose-style async middleware dispatch. Errors thrown by handlers are caught and routed to an `onError` callback if one is registered, but only for `Error` instances — anything else is re-thrown.

## Key Files

| File | Purpose |
|---|---|
| `src/index.ts` | Main entry point; re-exports Hono class, Context, HonoRequest, and types |
| `src/hono.ts` | `Hono` class — extends HonoBase, wires up SmartRouter with RegExpRouter + TrieRouter |
| `src/hono-base.ts` | `HonoBase` class — core routing, handler registration, request dispatch, error handling |
| `src/compose.ts` | Middleware composition engine (koa-compose pattern) |
| `src/context.ts` | `Context` class — wraps Request/Response, provides `c.json()`, `c.text()`, `c.html()`, etc. |
| `src/request.ts` | `HonoRequest` class — wraps the raw `Request` with parsed params, query, body helpers |
| `src/types.ts` | All framework type definitions (Env, Handler, MiddlewareHandler, Schema, etc.) |
| `src/router.ts` | `Router<T>` interface, HTTP method constants, `Result` type |
| `src/http-exception.ts` | `HTTPException` class for structured error responses |
| `src/router/reg-exp-router/` | Fastest router — compiles routes to RegExp patterns |
| `src/router/trie-router/` | Trie-based router — handles all route patterns |
| `src/router/smart-router/` | Meta-router that delegates to the best available router |
| `src/router/linear-router/` | Simple linear scan router |
| `src/router/pattern-router/` | Minimal pattern-matching router |
| `src/preset/tiny.ts` | Minimal preset using PatternRouter |
| `src/preset/quick.ts` | Preset using LinearRouter + TrieRouter via SmartRouter |
| `build/build.ts` | Custom esbuild-based build script |
| `vitest.config.ts` | Test configuration with multiple projects (default, jsx-runtime-default, jsx-runtime-dom, runtime tests) |
| `docs/CONTRIBUTING.md` | Contribution guidelines |

## Development Commands

```bash
# Install dependencies
bun install --frozen-lockfile

# Run full test suite (type-check + vitest)
bun run test

# Run tests in watch mode
bun run test:watch

# Run tests for a specific runtime
bun run test:deno
bun run test:bun
bun run test:node
bun run test:workerd
bun run test:fastly
bun run test:lambda
bun run test:lambda-edge
bun run test:all          # main + deno + bun

# Lint
bun run lint
bun run lint:fix

# Format
bun run format            # check only
bun run format:fix        # auto-fix

# Build
bun run build

# Coverage
bun run coverage
```

## Code Conventions

- **No semicolons**, single quotes, trailing commas (ES5 style) — enforced by Prettier
- **2-space indentation**, LF line endings — enforced by `.editorconfig`
- **Print width:** 100 characters
- **JSX:** single quotes in JSX (`jsxSingleQuote: true`)
- **Strict TypeScript** with `noEmit` for type-checking only (esbuild handles compilation)
- **No unused locals/parameters** enforced in build config (`tsconfig.build.json`) but relaxed in test config
- **Module resolution:** Bundler-style (`moduleResolution: "Bundler"`)
- **Import style:** relative imports only within src/; no path aliases
- **Export structure:** granular subpath exports in package.json (e.g., `hono/cors`, `hono/jwt`, `hono/cookie`) — each middleware/helper/adapter is independently importable
- **Zero runtime dependencies** — all functionality is self-contained

## Testing

- **Framework:** Vitest with globals enabled (no need to import `describe`, `it`, `expect`)
- **Setup file:** `.vitest.config/setup-vitest.ts`
- **Test file naming:** `*.test.ts` or `*.spec.ts`, co-located next to source files
- **JSX test projects:** two separate vitest projects test JSX with different import sources (`./src/jsx` and `./src/jsx/dom`)
- **Runtime tests:** separate test suites under `runtime-tests/` for Deno, Bun, Node.js, Cloudflare workerd, Fastly Compute, AWS Lambda, and Lambda@Edge
- **Coverage:** V8 provider, excludes benchmarks, runtime-tests, type-only files, and build scripts
- **CI matrix:** tests run on Node.js 18.18.2, 20.x, and 22.x; plus Deno, Bun (Linux + Windows), and platform-specific runtimes

## Known Issues or Gotchas

- **`compose.ts` error handling is selective:** only catches `Error` instances when an `onError` handler is registered. Non-Error throws (strings, objects) propagate uncaught. This is intentional.
- **`next()` called multiple times** in middleware triggers an explicit `throw new Error('next() called multiple times')` — a guard inherited from the koa-compose pattern.
- **SmartRouter fallback:** if `RegExpRouter` can't handle a route pattern, SmartRouter silently falls back to `TrieRouter`. Route registration errors from RegExpRouter are swallowed during this fallback.
- **Dual CJS/ESM output:** the build produces both ESM (`dist/`) and CJS (`dist/cjs/`) with a `package.json` containing `"type": "commonjs"` copied into `dist/cjs/`.
- **Platform-specific behavior:** adapter modules import platform-specific APIs; tests for these require their respective runtimes (Deno CLI, Bun, wrangler, etc.).
- **JSX is self-contained:** the `src/jsx/` subsystem has its own rendering engine, DOM implementation, and hooks — it does not use React. It has minimal imports from the rest of the framework.
- **Third-party middleware** lives in a separate repo (`honojs/middleware`), not here. This repo only contains first-party middleware.

## Recommended Reading Order for New Contributors

1. **`src/types.ts`** — understand `Env`, `Handler`, `MiddlewareHandler`, `Context` types
2. **`src/request.ts`** — `HonoRequest` wrapping the standard `Request`
3. **`src/context.ts`** — `Context` class and its response helpers (`c.json()`, `c.text()`, etc.)
4. **`src/router.ts`** — the `Router<T>` interface all routers implement
5. **`src/router/trie-router/`** — simplest router implementation to understand the routing contract
6. **`src/compose.ts`** — middleware composition (small file, critical to understand the pipeline)
7. **`src/hono-base.ts`** — core framework: route registration, request dispatch, error handling
8. **`src/hono.ts`** — the actual `Hono` class (thin wrapper over HonoBase with SmartRouter)
9. **`src/middleware/logger/`** — simple middleware example to see the middleware pattern
10. **`src/adapter/bun/` or `src/adapter/cloudflare-workers/`** — see how platform adapters bridge Hono to a runtime
11. **`docs/CONTRIBUTING.md`** — contribution workflow and third-party middleware policy
