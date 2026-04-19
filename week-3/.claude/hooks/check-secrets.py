#!/usr/bin/env python3
"""PreToolUse hook: Scan edits/writes for leaked secrets.

Matcher: Edit|Write
Reads JSON from stdin, checks tool_input.content or tool_input.new_string
against secret patterns. Blocks and logs if a match is found.
"""

import json
import re
import sys
import os
from datetime import datetime, timezone

SECRET_PATTERNS = [
    (r"(?:api[_-]?key|apikey)\s*[:=]\s*[\w-]{20,}", "API key"),
    (r"(?:password|passwd|pwd)\s*[:=]\s*[^\s]{8,}", "password"),
    (r"(?:secret|token)\s*[:=]\s*[\w-]{20,}", "secret/token"),
    (r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----", "private key"),
    (r"(?:sk|pk)[-_](?:live|test)[-_][a-zA-Z0-9_]{20,}", "Stripe-style key"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub personal access token"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key"),
]

def get_audit_dir():
    """Find the audit directory relative to this hook's location."""
    hook_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(hook_dir), "audit")

def log_block(pattern_name, file_path):
    """Append a timestamped entry to blocked.log."""
    audit_dir = get_audit_dir()
    os.makedirs(audit_dir, exist_ok=True)
    blocked_log = os.path.join(audit_dir, "blocked.log")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = f"[{timestamp}] BLOCKED check-secrets.py \"{file_path}\" reason=\"Potential {pattern_name} detected\"\n"
    with open(blocked_log, "a") as f:
        f.write(entry)

def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_input = data.get("tool_input", {})

    # Check both Write (content) and Edit (new_string) payloads
    content = tool_input.get("content", "") or tool_input.get("new_string", "")
    file_path = tool_input.get("file_path", "unknown")

    if not content:
        sys.exit(0)

    for pattern, name in SECRET_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            log_block(name, file_path)
            print(f"BLOCKED: Potential {name} detected in {file_path}", file=sys.stderr)
            sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
