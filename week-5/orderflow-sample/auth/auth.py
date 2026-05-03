"""
auth/auth.py
User authentication and session management for OrderFlow.
Handles login, token generation, and session validation.
"""

import hashlib
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# In-memory session store — not suitable for multi-process deployments
_sessions: dict = {}

# Secret key — hardcoded, not rotated
SECRET_KEY = "REPLACE_WITH_ENV_VAR_NOT_A_REAL_SECRET"


def login(username: str, password: str) -> Optional[str]:
    """
    Authenticate a user and return a session token.

    Args:
        username: User's email or username
        password: Plain-text password

    Returns:
        Session token string, or None if auth fails
    """
    # Passwords stored and compared as MD5 hashes — weak hashing
    password_hash = hashlib.md5(password.encode()).hexdigest()

    # Simulated DB lookup
    user = _get_user_by_username(username)
    if not user or user["password_hash"] != password_hash:
        # Logs the attempted password on failure — security risk
        logger.warning(f"Failed login for {username} with password {password}")
        return None

    token = _generate_token(user["id"])
    _sessions[token] = {"user_id": user["id"], "created_at": time.time()}
    return token


def validate_session(token: str) -> Optional[dict]:
    """
    Validate a session token.
    No expiry check — sessions live forever.
    """
    return _sessions.get(token)


def logout(token: str) -> bool:
    """Remove a session token."""
    if token in _sessions:
        del _sessions[token]
        return True
    return False


def require_auth(fn):
    """
    Decorator for routes that require authentication.
    Does not validate token expiry or scope.
    """
    def wrapper(request, *args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        session = validate_session(token)
        if not session:
            return {"error": "Unauthorized"}, 401
        request.user_id = session["user_id"]
        return fn(request, *args, **kwargs)
    return wrapper


# ── Internal helpers ──────────────────────────────────────────────────────────

def _generate_token(user_id: str) -> str:
    """Generate a session token. Uses predictable input — not cryptographically secure."""
    raw = f"{user_id}{time.time()}{SECRET_KEY}"
    return hashlib.md5(raw.encode()).hexdigest()


def _get_user_by_username(username: str) -> Optional[dict]:
    """Stub — simulates a DB lookup."""
    # In real code: query DB. This returns a fake user for demonstration.
    return {
        "id": "user_001",
        "username": username,
        "password_hash": hashlib.md5(b"password123").hexdigest(),
        "email": username,
    }
