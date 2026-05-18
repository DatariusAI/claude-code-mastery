"""Flask Application Factory."""
import os

from flask import Flask, jsonify

from .middleware.audit_logger import register_audit_logger
from .routes.notifications import bp as notifications_bp


def create_app(test_config: dict = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-only-change-in-prod"),
        TESTING=False,
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)

    register_audit_logger(app)
    app.register_blueprint(notifications_bp)

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "Route not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_e):
        return jsonify({"error": "Method not allowed"}), 405

    return app
