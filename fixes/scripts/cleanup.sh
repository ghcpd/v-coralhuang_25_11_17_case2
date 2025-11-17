#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/.." >/dev/null 2>&1 && pwd)"

rm -rf "$ROOT_DIR/artifacts"
mkdir -p "$ROOT_DIR/artifacts"
echo "Cleared artifacts under $ROOT_DIR/artifacts"

if [[ "${1:-}" == "--venv" ]]; then
  rm -rf "$ROOT_DIR/.venv"
  echo "Removed virtual environment at $ROOT_DIR/.venv"
fi
