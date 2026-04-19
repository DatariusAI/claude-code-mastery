# /ship Pipeline Flow

```mermaid
flowchart LR
    subgraph invoke["Developer invokes /ship"]
        A["Stage 1\n/review"]
    end

    A -->|PASS| B["Stage 2\n/test-gen"]
    A -->|"FAIL\n(error findings)"| X1["❌ Pipeline\nAborted"]

    B -->|PASS| C["Stage 3\n/commit"]
    B -->|"FAIL\n(tests fail)"| X2["❌ Pipeline\nAborted"]

    C -->|SUCCESS| D["Stage 4\ngh pr create"]
    C -->|"FAIL\n(hook block)"| X3["❌ Pipeline\nAborted"]

    D --> E["✅ PR Created\nwith review findings\n+ coverage data\n+ governance metadata"]
    D --> F["📝 Results saved\naudit/ship-sample-run.md"]

    style A fill:#58a6ff,color:#fff,stroke:#1f6feb
    style B fill:#bc8cff,color:#fff,stroke:#8b5cf6
    style C fill:#f778ba,color:#fff,stroke:#db61a2
    style D fill:#3fb950,color:#fff,stroke:#238636
    style E fill:#238636,color:#fff,stroke:#196c2e
    style F fill:#161b22,color:#8b949e,stroke:#30363d
    style X1 fill:#da3633,color:#fff,stroke:#b62324
    style X2 fill:#da3633,color:#fff,stroke:#b62324
    style X3 fill:#da3633,color:#fff,stroke:#b62324
```

## Key Design Decisions

- **Fail-fast ordering:** /review (fast, cheap) runs before /test-gen (slow, expensive)
- **Hard gates:** Any stage failure aborts the entire pipeline — no partial PRs
- **Audit trail:** Every run is recorded in `ship-sample-run.md` regardless of outcome
- **PR enrichment:** The PR body includes review findings and coverage data from earlier stages
