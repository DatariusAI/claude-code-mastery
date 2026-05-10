# ─────────────────────────────────────────────────────────────────────────────
# HealthTrack API — Production container image
#
# Multi-stage build:
#   1. builder  (python:3.11)         — installs deps into /install
#   2. runtime  (python:3.11-slim)    — copies only compiled deps + source
#
# Security posture:
#   - Runs as non-root user `appuser` (UID 10001).
#   - Uses gunicorn (production WSGI), NOT the Flask dev server.
#   - HEALTHCHECK uses python's stdlib urllib so the runtime image stays
#     curl-free and ~10MB smaller.
#   - PYTHONDONTWRITEBYTECODE / PYTHONUNBUFFERED set so logs flush
#     immediately and no .pyc files clutter the layered fs.
#
# See REPORT.md for design-decision rationale (why gunicorn, why urllib).
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: builder ─────────────────────────────────────────────────────────
# Full python:3.11 image because pip wheel-building sometimes needs gcc/make.
FROM python:3.11 AS builder

# Install Python deps into a target prefix so the runtime stage can copy
# just /install and skip everything else (apt cache, build tools, etc.).
WORKDIR /build
COPY requirements.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
# Slim image keeps the runtime layer small (no build toolchain, no docs).
FROM python:3.11-slim AS runtime

# Don't write .pyc files; flush stdout/stderr immediately for clean logs.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Create a non-root user. Numeric UID makes the image work cleanly when
# Kubernetes / orchestrators enforce runAsNonRoot with a numeric range.
RUN useradd --create-home --uid 10001 --user-group appuser

# Copy installed Python deps from the builder stage. /install is what
# `pip install --prefix=/install` populated; layering it under /usr/local
# is the standard slim-runtime pattern.
COPY --from=builder /install /usr/local

# Copy application source. .dockerignore keeps tests/, .git/, .env, etc. out.
WORKDIR /app
COPY --chown=appuser:appuser . /app

# Drop root before launching the app process. All RUN/COPY steps that
# need root must come BEFORE this line.
USER appuser

# Document the listening port for orchestrators / readers.
EXPOSE 5000

# CHANGED FROM CLAUDE OUTPUT: python urllib replaces curl
# (python:3.11-slim has no curl by default; using urllib avoids
#  an apt-get install step that would add ~10MB to the runtime image.)
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:5000/health',timeout=5).status==200 else 1)"

# CHANGED FROM CLAUDE OUTPUT: gunicorn replaces flask dev server
# (Flask's built-in server prints "WARNING: This is a development server"
#  and is unsafe for any non-local use. gunicorn 21+ supports the Flask
#  application-factory pattern via the `app:create_app()` callable form.)
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:create_app()"]
