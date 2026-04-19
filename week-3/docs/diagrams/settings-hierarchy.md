# Settings Hierarchy

```mermaid
flowchart TD
    E["🏢 Enterprise\nsettings.json\n(org-wide, admin-managed)"]
    P["📁 Project\n.claude/settings.json\n(checked into repo)"]
    U["👤 User\n~/.claude/settings.json\n(personal preferences)"]
    L["💻 Local\n.claude/settings.local.json\n(gitignored, machine-specific)"]

    E -->|overrides| P
    P -->|overrides| U
    U -->|overrides| L

    P -.->|"⬅ THIS FILE\nGovernance hooks &\npermission rules live here\nbecause they must be\nshared across all devs"| Note["Why Project Tier?\n• Version-controlled\n• Peer-reviewed\n• Consistent for team\n• CI/CD can validate"]

    style E fill:#da3633,color:#fff,stroke:#b62324
    style P fill:#58a6ff,color:#fff,stroke:#1f6feb
    style U fill:#bc8cff,color:#fff,stroke:#8b5cf6
    style L fill:#484f58,color:#fff,stroke:#30363d
    style Note fill:#161b22,color:#8b949e,stroke:#30363d
```

## What Goes Where

| Tier | Example Content | Who Manages |
|------|----------------|-------------|
| **Enterprise** | "Never allow `Bash(rm -rf /)`" across all repos | Platform/Security team |
| **Project** | Hook definitions, permission allow/deny lists, cost limits | Tech lead, code-reviewed |
| **User** | Preferred model, output verbosity, theme | Individual developer |
| **Local** | Machine-specific paths, local API keys (gitignored) | Individual developer |

## Override Rules

- Higher tiers **cannot be overridden** by lower tiers
- Enterprise policies are absolute — no project or user setting can weaken them
- Project-level hooks run for every developer who clones the repo
- User and Local settings only add restrictions or personal preferences
