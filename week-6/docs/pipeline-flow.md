# Pipeline Flow — Developer to Merge

End-to-end sequence: a developer commits a change, GitHub Actions runs the
4-job pipeline, the AI-Skill review parses the Security Audit Skill output,
and the merge gate decides eligibility.

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Local as Local repo
    participant GH as GitHub
    participant CI as ci.yml
    participant Skill as Security Audit Skill
    participant Gate as Merge gate

    Dev->>Local: edit + git commit
    Local->>GH: git push
    Dev->>GH: gh pr create
    GH->>CI: trigger (pull_request to main)

    rect rgba(31,111,235,0.15)
    note over CI: Stage 1
    CI->>CI: lint &mdash; flake8 + black
    end

    rect rgba(63,185,80,0.15)
    note over CI: Stage 2 (parallel)
    par
        CI->>CI: test &mdash; pytest --cov ≥ 80%
    and
        CI->>CI: security &mdash; bandit + safety
    end
    end

    rect rgba(188,140,255,0.15)
    note over CI,Skill: Stage 3
    CI->>Skill: python plugins/run_skill.py security-audit<br/>--scope app/vitals.py --context CLAUDE.md
    Skill-->>CI: JSON findings array
    CI->>CI: parse JSON, count CRITICAL findings
    end

    alt no CRITICAL findings
        CI->>Gate: exit 0
        Gate-->>GH: green check
        GH-->>Dev: ready to merge
    else CRITICAL finding present
        CI->>Gate: exit 1<br/>(BLOCKED: N CRITICAL finding(s))
        Gate-->>GH: red X
        GH-->>Dev: merge BLOCKED
    end
```

Job summaries from each stage are written to `$GITHUB_STEP_SUMMARY`, so
the run page surfaces the whole pipeline status without expanding logs.
