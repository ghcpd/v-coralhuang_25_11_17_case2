#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
  echo "Virtual environment missing. Run ./setup.sh first." >&2
  exit 1
fi
source "$SCRIPT_DIR/.venv/bin/activate"
cd "$SCRIPT_DIR/.."
pytest -s fixes/tests
