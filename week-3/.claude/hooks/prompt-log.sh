#!/usr/bin/env bash
# UserPromptSubmit hook: Log all user prompts to prompts.jsonl.
#
# Matcher: *
# Appends a JSONL entry with timestamp and the raw prompt text.

set -euo pipefail

AUDIT_DIR="$(cd "$(dirname "$0")/.." && pwd)/audit"
PROMPT_LOG="${AUDIT_DIR}/prompts.jsonl"
mkdir -p "${AUDIT_DIR}"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Truncate very long prompts to keep log manageable
PROMPT_TRUNCATED=$(echo "${CLAUDE_USER_PROMPT:-}" | head -c 1000)

python -c "
import json, sys
entry = {
    'timestamp': sys.argv[1],
    'prompt': sys.argv[2]
}
print(json.dumps(entry))
" "${TIMESTAMP}" "${PROMPT_TRUNCATED}" \
  >> "${PROMPT_LOG}"
