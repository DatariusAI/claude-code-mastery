"""
HealthTrack API
A patient vitals tracking backend for clinics.
"""
import os

from flask import Flask
import psycopg2
import redis

from .routes import vitals_bp, patients_bp, alerts_bp


def create_app():
    app = Flask(__name__)
    # ──────────────────────────────────────────────────────────────
    # TEACHING FIXTURE — DO NOT REMOVE OR SANITIZE
    # This intentionally-hardcoded value triggers a CRITICAL finding
    # from the Security Audit Skill so the CI gate
    # ("Block merge if output contains CRITICAL") has something
    # to fire on. See SECURITY_FIXTURES.md.
    # Real production code MUST load this from an environment
    # variable; this fixture exists ONLY for the Week 6 mini-project
    # CI gate exercise.
    # ──────────────────────────────────────────────────────────────
    app.config["SECRET_KEY"] = "dev-secret-change-in-prod"
    app.register_blueprint(vitals_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(alerts_bp)

    @app.get("/health")
    def health():
        # Liveness + readiness probe.
        #
        # Returns 200 + {"status": "ok", "checks": {...}} when the database
        # and cache are both reachable. Returns 503 + {"status": "degraded",
        # ...} if either fails — the orchestrator can then route traffic
        # away or restart the container. Sub-checks are run in-line (cheap)
        # rather than via a periodic background poll so a fresh container
        # never reports healthy until its dependencies actually answer.
        checks = {}
        overall_ok = True

        # Database check
        try:
            conn = psycopg2.connect(
                host=os.environ.get("DB_HOST", "db"),
                port=int(os.environ.get("DB_PORT", "5432")),
                dbname=os.environ.get("DB_NAME", "healthtrack"),
                user=os.environ.get("DB_USER", "healthtrack"),
                password=os.environ.get("DB_PASSWORD", ""),
                connect_timeout=2,
            )
            conn.close()
            checks["database"] = "ok"
        except Exception:
            checks["database"] = "fail"
            overall_ok = False

        # Cache check
        try:
            r = redis.Redis.from_url(
                os.environ.get("REDIS_URL", "redis://cache:6379/0"),
                socket_connect_timeout=2,
            )
            r.ping()
            checks["cache"] = "ok"
        except Exception:
            checks["cache"] = "fail"
            overall_ok = False

        status = "ok" if overall_ok else "degraded"
        http_code = 200 if overall_ok else 503
        return {"status": status, "checks": checks}, http_code

    return app
