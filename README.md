# Mini Project 1 — Codebase Detective: Hono

An AI-assisted deep dive into the [Hono](https://github.com/honojs/hono) web framework's source code, produced using Claude Code.

## What's Inside

```
.
├── CLAUDE.md                              # Comprehensive project guide for Hono
├── docs/
│   ├── reflections.md                     # Q1-Q12 prompt engineering reflections
│   └── visualization/
│       └── dependency-graph.html          # Interactive D3.js dependency map (184 nodes, 470 edges)
└── README.md
```

## Artifacts

### CLAUDE.md
A complete onboarding guide generated from actual source code analysis. Covers project overview, tech stack, architecture (layered dependency model), key files, development commands, code conventions, testing setup, gotchas, and a recommended reading order for new contributors.

### Dependency Graph (`docs/visualization/dependency-graph.html`)
A self-contained, interactive force-directed graph of all module dependencies in Hono's `src/` directory. Open directly in any browser — no server required.

Features:
- 184 nodes (every `.ts` file) connected by 470 directed edges (every relative import)
- Color-coded by directory: core, middleware, router, utils, adapter, helper, jsx, client
- Node size scaled by number of incoming imports
- Hover to highlight connections and show full file path
- Search box to filter and highlight nodes
- Draggable nodes, zoomable/pannable canvas
- Dark background (#1a1a2e) with white labels

### Reflections (`docs/reflections.md`)
12 questions exploring AI behavior, limitations, hallucination patterns, prompt engineering techniques, and lessons learned during the investigation session.

## Key Findings

- Hono has **zero production dependencies** — everything is built from scratch on Web Standards
- The architecture follows clean layering: `utils → router → core → helpers → middleware → adapters`
- Five router implementations exist, with `SmartRouter` auto-selecting the fastest one at runtime
- The middleware pipeline in `compose.ts` (73 lines) is the single most important file to understand
- The JSX subsystem is largely self-contained with minimal imports from the rest of the framework

## Target Repository

- **Repo:** [honojs/hono](https://github.com/honojs/hono)
- **Version analyzed:** 4.12.9
- **Files analyzed:** 184 TypeScript source files across 11 directories
