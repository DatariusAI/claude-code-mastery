#!/usr/bin/env python3
"""PreToolUse hook: Block dangerous bash commands.

Matcher: Bash
Reads JSON from stdin, extracts tool_input.command.
Blocks destructive patterns and exits 1 with stderr message.
Appends blocked actions to audit/blocked.log.
"""

import json
import re
import sys
import os
from datetime import datetime, timezone

BLOCKED_PATTERNS = [
    (r"rm\s+-rf\b", "rm -rf (recursive force delete)"),
    (r"DROP\s+TABLE\b", "DROP TABLE"),
    (r"DROP\s+DATABASE\b", "DROP DATABASE"),
    (r"git\s+push\s+--force\b", "git push --force"),
    (r"git\s+reset\s+--hard\b", "git reset --hard"),
    (r"chmod\s+777\b", "chmod 777 (world-writable)"),
    (r"curl\s+.*\|\s*bash\b", "curl | bash (remote code execution)"),
    (r"curl\s+.*\|\s*sh\b", "curl | sh (remote code execution)"),
    (r"wget\s+.*\|\s*sh\b", "wget | sh (remote code execution)"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key pattern"),
]

def get_audit_dir():
    """Find the audit directory relative to this hook's location."""
    hook_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(hook_dir), "audit")

def log_block(pattern_name, command):
    """Append a timestamped entry to blocked.log."""
    audit_dir = get_audit_dir()
    os.makedirs(audit_dir, exist_ok=True)
    blocked_log = os.path.join(audit_dir, "blocked.log")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = f"[{timestamp}] BLOCKED validate-bash.py \"{command[:80]}\" reason=\"{pattern_name}\"\n"
    with open(blocked_log, "a") as f:
        f.write(entry)

def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command:
        sys.exit(0)

    for pattern, name in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            log_block(name, command)
            print(f"BLOCKED: {name}", file=sys.stderr)
            sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
