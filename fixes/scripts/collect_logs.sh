#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
mkdir -p artifacts
ARTIFACT_LOG="$(pwd)/artifacts/tests.log"
./run_test.sh > "$ARTIFACT_LOG" 2>&1
