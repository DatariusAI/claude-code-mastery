#!/usr/bin/env bash
# PreToolUse hook: Enforce file scope for Edit and Write operations.
#
# Matcher: Edit|Write
# Reads $CLAUDE_TOOL_INPUT, extracts file_path via python (portable).
# Allows edits only to approved paths; blocks everything else.
# Appends blocked actions to audit/blocked.log.

set -euo pipefail

AUDIT_DIR="$(cd "$(dirname "$0")/.." && pwd)/audit"
BLOCKED_LOG="${AUDIT_DIR}/blocked.log"
mkdir -p "${AUDIT_DIR}"

# Extract file_path from tool input JSON using python (no jq dependency)
FILE_PATH=$(python -c "import json,sys; d=json.loads(sys.argv[1]); print(d.get('file_path',''))" "${CLAUDE_TOOL_INPUT}" 2>/dev/null || echo "")

if [ -z "${FILE_PATH}" ]; then
  exit 0
fi

# Normalize to relative path from repo root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
REL_PATH="${FILE_PATH#${REPO_ROOT}/}"
REL_PATH="${REL_PATH#./}"

log_block() {
  local reason="$1"
  echo "BLOCKED: Cannot edit ${REL_PATH} — ${reason}" >&2
  echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] BLOCKED scope-guard.sh \"${REL_PATH}\" reason=\"${reason}\"" >> "${BLOCKED_LOG}"
  exit 1
}

# --- ALWAYS BLOCK these patterns ---
case "${REL_PATH}" in
  .env|.env.*|credentials.json|secrets.yaml)
    log_block "sensitive file"
    ;;
  *.pem|*.key)
    log_block "key/certificate file"
    ;;
  docker-compose.prod.yml)
    log_block "production config"
    ;;
  .github/workflows/*)
    log_block "CI/CD pipeline"
    ;;
  package.json)
    # Root package.json is blocked; week-3/*/package.json passes through to allow check below
    log_block "root package.json"
    ;;
  week-1/*|week-2/*)
    log_block "frozen completed week"
    ;;
  docs/*)
    log_block "root docs/ is Week 1 owned, frozen"
    ;;
esac

# --- ALLOW these path prefixes ---
case "${REL_PATH}" in
  week-3/sample-target/*|week-3/.claude/*|week-3/docs/*|week-3/tests/*)
    exit 0
    ;;
  week-3/CLAUDE.md|week-3/README.md|week-3/REPORT.md|week-3/.gitignore)
    exit 0
    ;;
  index.html)
    # Dashboard updates allowed
    exit 0
    ;;
esac

# Default: block anything not explicitly allowed
log_block "path not in allowlist"
