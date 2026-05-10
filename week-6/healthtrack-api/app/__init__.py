"""
HealthTrack API
A patient vitals tracking backend for clinics.
"""
from flask import Flask
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
    return app
