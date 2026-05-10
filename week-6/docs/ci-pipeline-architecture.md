# CI Pipeline Architecture

The Week 6 CI pipeline runs on every pull request and every push to `main`.
Four jobs with explicit `needs:` ordering form a dependency DAG:
`lint → {test, security} → ai-skills`. The AI-Skill job parses the Security
Audit Skill output and exits non-zero on any `CRITICAL` finding, blocking
the merge.

```mermaid
flowchart LR
    PR([PR opened / push to main]) --> LINT[<b>lint</b><br/>flake8 + black]
    LINT --> TEST[<b>test</b><br/>pytest --cov ≥ 80%]
    LINT --> SEC[<b>security</b><br/>bandit + safety]
    TEST --> AI[<b>ai-skills</b><br/>Security Audit Skill<br/>on app/vitals.py]
    SEC --> AI
    AI -->|no CRITICAL| GREEN([green check<br/>merge ready])
    AI -->|CRITICAL found| BLOCK([red X<br/>merge BLOCKED])

    classDef gate fill:#bc8cff,stroke:#3fb950,color:#000
    classDef block fill:#f85149,stroke:#f85149,color:#fff
    classDef ok fill:#3fb950,stroke:#3fb950,color:#000
    class AI gate
    class BLOCK block
    class GREEN ok
```

Coverage and CRITICAL gates both fail the pipeline; only one needs to fire
to block merge. The PR template's checkboxes (Security, Performance,
Migrations, Feature Flags) are an additional non-automated gate.
