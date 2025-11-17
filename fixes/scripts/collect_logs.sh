#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <label> <command> [args...]" >&2
  exit 2
fi

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/.." >/dev/null 2>&1 && pwd)"
LABEL="$1"
shift

mkdir -p "$ROOT_DIR/artifacts"
LOG_FILE="$ROOT_DIR/artifacts/${LABEL}.log"

set +e
"$@" >"$LOG_FILE" 2>&1
STATUS=$?
set -e

{
  echo
  echo "Command: $*"
  echo "Exit status: $STATUS"
} >>"$LOG_FILE"

cat "$LOG_FILE"
exit $STATUS
