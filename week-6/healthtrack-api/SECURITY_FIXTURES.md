# Teaching Fixtures — Intentional Hardcoded Secrets

## Why these exist

The HealthTrack scaffold for the Week 6 mini project ships with four
intentionally-hardcoded secret-shaped string literals. They are
**teaching fixtures**, not real credentials. The Week 6 CI pipeline
includes an AI-Skill gate that runs the Security Audit Skill against
`app/vitals.py` and **blocks merge if the output contains
`CRITICAL`**. That gate needs something to fire on. Sanitising these
literals — replacing them with `os.environ.get(...)` placeholders the
way Week 5 OrderFlow did — would silence the auditor and leave the
gate untestable. So we keep them as-is, document the choice here, and
exempt them from secret scanning so push protection doesn't reject
honest commits.

## The 4 fixture lines

Line numbers reflect post-banner positions (each literal sits below a
10-line `TEACHING FIXTURE` banner comment).

| File | Line | Literal | OWASP category | What Security Audit Skill flags |
|---|---:|---|---|---|
| `app/auth.py` | 30 | `JWT_SECRET = "HealthTrack$JWT$2024"` | A02 — Cryptographic Failures | Hardcoded JWT signing secret; rotation impossible; predictable token forgery if leaked |
| `app/vitals.py` | 33 | `DB_PASSWORD = "Adm1n$ecure2024"` | A05 — Security Misconfiguration | Production DB password in source; bypasses secret-management; visible in any clone or git history |
| `app/alerts.py` | 27 | `SMS_API_KEY  = "sms_live_key_abc123xyz"` | A05 — Security Misconfiguration | Live-prefixed third-party API key in source; vendor key-rotation requires source change + redeploy |
| `app/__init__.py` | 21 | `SECRET_KEY = "dev-secret-change-in-prod"` | A02 — Cryptographic Failures | Flask session-signing key hardcoded; cookie forgery possible; same key across all environments |

## What real production code does instead

```python
# app/__init__.py — production-shaped pattern
import os
from flask import Flask


def create_app():
    app = Flask(__name__)

    secret_key = os.environ.get("FLASK_SECRET_KEY")
    if not secret_key:
        raise RuntimeError(
            "FLASK_SECRET_KEY is required at startup. "
            "Set it in the deployment environment; never hardcode."
        )
    app.config["SECRET_KEY"] = secret_key

    # ... blueprint registration ...
    return app
```

The same shape applies to `JWT_SECRET`, `DB_PASSWORD`, and
`SMS_API_KEY`: read from `os.environ`, fail loudly at startup if
missing, never commit a real value, and document required variables
in `.env.example`.

## Push protection note

GitHub's push protection scans for credential patterns on every push.
The first push of this branch will likely be rejected because
`sms_live_key_abc123xyz` matches a generic SMS-provider live-key
heuristic, and `Adm1n$ecure2024` may match strong-password regexes.

When that happens:

1. The rejection message prints an unblock URL of the form
   `https://github.com/<org>/<repo>/security/secret-scanning/unblock-secret/<id>`
2. Save that URL to `week-6/evidence/push-protection-unblock.txt`
   along with a 2-sentence note explaining the fixture context
3. Open the URL in a browser
4. Classify the push as **"Used in tests"** (or the closest
   equivalent the UI offers — "False positive" is also acceptable
   since these strings target a teaching fixture, not a real system)
5. Confirm the unblock
6. `git push` again — should succeed

This is documented in evidence/ so the rationale is captured next to
the action, not lost in git history.

## CodeQL exemption

Secret scanning and CodeQL are two separate scanners with separate
exemption files. The fixture literals also produce CodeQL alerts on
the *consequence* of hardcoding (MD5 password hashing in
`auth.py:_make_token`, clear-text password logging in
`auth.py:login`, SQL queries with PII in `vitals.py` debug logs) —
not just the credential strings themselves. CodeQL's PR check is
configured to block merges on new alerts, so without an exemption
every Week 6 PR would be blocked by the same teaching defects.

The repo-root file `.github/codeql/codeql-config.yml` has been
extended with a `paths-ignore` entry for `week-6/healthtrack-api/app/**`
that mirrors the existing `week-5/orderflow-sample/**` exemption.
The scope is **deliberately narrow**: only `app/` is exempted.
The Dockerfile, `docker-compose.yml`, `ci.yml`, `plugins/`,
`scripts/`, and `tests/` all stay under CodeQL coverage so any
real bug introduced there is caught.

Existing alerts on the same files are dismissed via the API with
reason `won't fix` and a comment pointing at this document. The
audit trail is preserved in the alert's dismissal metadata.

## Lifetime

These fixtures live **ONLY** in `week-6/`. They must NEVER be copied
to other weeks or to any production repository. Week 7 (Capstone)
must use environment-variable-loaded secrets, not these literals.
Both `.github/secret_scanning.yml` (in `week-6/healthtrack-api/.github/`)
and `.github/codeql/codeql-config.yml` (at repo root) `paths-ignore`
lists are scoped to the same four-file `app/` directory precisely
so that the exemption can't silently spread.
