"""
Server Entry Point
==================
Run from the project root:

    python run.py          (Windows PowerShell / Mac / Linux)

This works because the project root is automatically added to sys.path,
so `src` resolves as a package and all relative imports inside it work.
"""
import os
import signal
import sys

from src.app import create_app
from src.utils.logger import logger

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_ENV", "development") == "development"

    logger.info(
        "Notification Service starting",
        port=port,
        environment=os.getenv("FLASK_ENV", "development"),
        email_provider=os.getenv("EMAIL_PROVIDER", "mock"),
    )

    def _shutdown(sig, frame):
        logger.info("Shutdown signal received — exiting cleanly")
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    app.run(host="0.0.0.0", port=port, debug=debug)
