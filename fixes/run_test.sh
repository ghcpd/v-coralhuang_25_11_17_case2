#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Virtual environment not found at $VENV_DIR. Run fixes/setup.sh first." >&2
  exit 1
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

mkdir -p "$ROOT_DIR/artifacts"
LOG_FILE="$ROOT_DIR/artifacts/pytest.log"

export PYTHONPATH="$ROOT_DIR/src:${PYTHONPATH:-}"
set +e
pytest -s "$ROOT_DIR/tests" -vv "$@" 2>&1 | tee "$LOG_FILE"
STATUS=${PIPESTATUS[0]}
set -e
echo "Pytest finished with status $STATUS (log: $LOG_FILE)"
exit $STATUS
