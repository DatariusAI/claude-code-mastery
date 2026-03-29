# Hono Module Dependency Map

> **Interactive version:** Open [`dependency-graph.html`](./dependency-graph.html) locally in a browser for the full 184-node, 470-edge force-directed graph with search, tooltips, and drag.

## Directory-Level Dependencies

Import counts between top-level directories (edges with fewer than 2 imports omitted for clarity):

```mermaid
flowchart TB
    utils["utils<br/>26 files"]
    router["router<br/>15 files"]
    core["core<br/>9 files<br/>(types, context, request,<br/>compose, hono-base, hono)"]
    helper["helper<br/>25 files"]
    middleware["middleware<br/>34 files"]
    adapter["adapter<br/>37 files"]
    jsx["jsx<br/>27 files"]
    client["client<br/>5 files"]
    preset["preset<br/>2 files"]
    validator["validator<br/>3 files"]

    core -->|15| utils
    core -->|3| router
    router -->|8| core
    router -->|4| utils

    helper -->|27| core
    helper -->|18| utils
    helper -->|3| client

    middleware -->|53| core
    middleware -->|26| utils
    middleware -->|5| helper

    adapter -->|21| core
    adapter -->|13| helper
    adapter -->|3| middleware
    adapter -->|2| utils

    client -->|6| core
    client -->|5| utils

    jsx -->|10| utils
    jsx -->|7| helper

    preset -->|4| core
    preset -->|4| router

    validator -->|4| core
    validator -->|3| utils

    style utils fill:#8d99ae,color:#fff,stroke:#8d99ae
    style router fill:#ff9f1c,color:#fff,stroke:#ff9f1c
    style core fill:#4361ee,color:#fff,stroke:#4361ee
    style helper fill:#f15bb5,color:#fff,stroke:#f15bb5
    style middleware fill:#2ec4b6,color:#fff,stroke:#2ec4b6
    style adapter fill:#9b5de5,color:#fff,stroke:#9b5de5
    style jsx fill:#00f5d4,color:#000,stroke:#00f5d4
    style client fill:#fee440,color:#000,stroke:#fee440
    style preset fill:#c1121f,color:#fff,stroke:#c1121f
    style validator fill:#c1121f,color:#fff,stroke:#c1121f
```

## Most-Imported Modules (Hub Files)

These files are the most depended-upon across the codebase:

```mermaid
flowchart LR
    subgraph Top10["Most-Imported Files"]
        context["context.ts<br/>~58 importers"]
        hono["hono.ts<br/>~47 importers"]
        types["types.ts<br/>~44 importers"]
        router_if["router.ts<br/>~14 importers"]
        http_exc["http-exception.ts<br/>~14 importers"]
        conninfo["helper/conninfo<br/>~11 importers"]
    end

    middleware_dir["34 middleware files"] -->|53| context
    adapter_dir["37 adapter files"] -->|21| context
    helper_dir["25 helper files"] -->|27| context

    middleware_dir -->|types| types
    adapter_dir -->|types| types

    adapter_dir -->|conninfo| conninfo

    style context fill:#e94560,color:#fff
    style types fill:#e94560,color:#fff
    style hono fill:#e94560,color:#fff
    style router_if fill:#4361ee,color:#fff
    style http_exc fill:#4361ee,color:#fff
    style conninfo fill:#f15bb5,color:#fff
```

## Key Observations

- **`middleware/` → `core/`** is the heaviest dependency edge (53 imports) — every middleware imports Context and types
- **`utils/`** is the true foundation layer with zero upward dependencies (only 1 edge to core, likely a type import)
- **`jsx/`** is nearly isolated — only imports from `utils/` and `helper/`, never from `core/` directly
- **`adapter/`** depends on `core/` + `helper/` but never on other adapters (clean platform separation)
- **`context.ts`** is the single most-imported file in the entire codebase (~58 importers)
