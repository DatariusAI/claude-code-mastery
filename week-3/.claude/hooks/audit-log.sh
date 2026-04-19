#!/usr/bin/env bash
# PostToolUse hook: Log every tool action to audit.jsonl.
#
# Matcher: *
# Appends a JSONL entry with timestamp, user, branch, tool, input, result.

set -euo pipefail

AUDIT_DIR="$(cd "$(dirname "$0")/.." && pwd)/audit"
AUDIT_LOG="${AUDIT_DIR}/audit.jsonl"
mkdir -p "${AUDIT_DIR}"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
USER=$(whoami 2>/dev/null || echo "unknown")
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")

# Truncate large inputs/results to keep log entries manageable
TOOL_INPUT_TRUNCATED=$(echo "${CLAUDE_TOOL_INPUT:-}" | head -c 500)
TOOL_RESULT_TRUNCATED=$(echo "${CLAUDE_TOOL_RESULT:-}" | head -c 500)

# Build JSONL entry using python for proper JSON escaping (portable, no jq)
python -c "
import json, sys
entry = {
    'timestamp': sys.argv[1],
    'user': sys.argv[2],
    'branch': sys.argv[3],
    'tool': sys.argv[4],
    'input': sys.argv[5],
    'result': sys.argv[6]
}
print(json.dumps(entry))
" "${TIMESTAMP}" "${USER}" "${BRANCH}" "${CLAUDE_TOOL_NAME:-unknown}" "${TOOL_INPUT_TRUNCATED}" "${TOOL_RESULT_TRUNCATED}" \
  >> "${AUDIT_LOG}"
