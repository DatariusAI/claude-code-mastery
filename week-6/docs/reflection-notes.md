# Reflection Notes — Week 6 Mini Project

Answers to the brief's Section 4.3 four reflection questions. Compiled while
the work was fresh; feeds REPORT.md (full version) and the submission PDF.

## 1. Hardest part of setting up the CI pipeline

The brief's Part 1.1 prompt produces a working ci.yml in one shot, but the
`needs:` graph and the AI-Skill CRITICAL gate are easy to get *almost*
right and have it look fine until the first PR runs. The real friction was
deciding where ci.yml should live: GitHub Actions only triggers from
`.github/workflows/` at the **repo root**, not from inside `week-6/healthtrack-api/`.
The submitted artifact stays inside the project per the brief's rubric, so
Session D needs a thin trigger workflow at the repo root that re-runs the
same pipeline with `working-directory: week-6/healthtrack-api`. That
indirection wasn't obvious from the prompt — I caught it because Session A's
ci.yml already had `defaults.run.working-directory` set, which only makes
sense if the file is *eventually* moved to repo root.

## 2. What the Docker healthcheck caught that host curl didn't

A host-side `curl http://localhost:5000/health` only proves the app
is reachable on the bound port — it tells you nothing about whether the
container's own networking is healthy from *inside*. The Dockerfile's
HEALTHCHECK runs `python -c "urllib.request.urlopen(...)"` *inside* the
container with `localhost`, so it exercises the loopback interface and the
gunicorn worker pool from the same routing path Kubernetes / docker-compose
will probe in production. The access logs proved it: `Python-urllib/3.11
GET /health` lines fired every 30 seconds whether or not I curled from the
host. A healthy host curl with an unhealthy container HEALTHCHECK would
mean the app is reachable but the container will be killed on its next
liveness check — exactly the kind of split-brain a host-only test misses.

## 3. One thing changed in Claude's output and why

The Dockerfile prompt explicitly asked for `HEALTHCHECK CMD curl -f
http://localhost:5000/health`, and Claude generated exactly that. But
`python:3.11-slim` ships without curl; the HEALTHCHECK would have failed
inside the runtime stage with `curl: not found`. Two fixes were possible:
`apt-get install curl` (~10 MB image bloat) or the stdlib `urllib.request`
(zero new packages). I picked urllib and documented the change inline with
a `# CHANGED FROM CLAUDE OUTPUT:` comment so a reviewer can see the
deviation without reading the brief. Same pattern for the `flask run` →
`gunicorn` swap — Flask's dev server prints "WARNING: This is a development
server" and is unsafe for any non-local use; gunicorn 21+ accepts the
factory pattern via `app:create_app()`.

## 4. What you'd add with another hour

Three things, in priority order: (1) the thin `.github/workflows/week-6-ci.yml`
trigger at repo root, so Session D doesn't have to invent it; (2) a
`docker-compose.override.yml` that mounts `./app` as a bind volume for
hot-reload local dev — the current setup rebuilds the image for every
source change, which is fine for CI but slow when iterating on routes;
(3) a structured logging shim (`structlog` or `python-json-logger`) so
the gunicorn access lines emit JSON instead of Apache combined-log format,
which makes the Docker HEALTHCHECK access lines grep-friendly when
debugging health-flap incidents.
