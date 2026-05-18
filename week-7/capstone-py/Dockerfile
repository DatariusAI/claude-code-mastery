# ============================================================
# Dockerfile — Notification Service (Python/Flask)
# Generated via Claude Code — capstone deployment artifact
# ============================================================

# ── Stage 1: Build deps ──────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Production runtime ─────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Security: non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY --chown=appuser:appgroup src/ ./src/

USER appuser

EXPOSE 5000

# Health check (REQ-005)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')" \
    || exit 1

CMD ["python", "src/run.py"]
