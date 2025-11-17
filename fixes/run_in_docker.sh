#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="flask-translate-fix"
docker build -f "$SCRIPT_DIR/Dockerfile.fix" -t "$IMAGE_NAME" .
docker run --rm \
  -v "$SCRIPT_DIR/artifacts":/workspace/fixes/artifacts \
  "$IMAGE_NAME" \
  /bin/bash -c "cd /workspace && ./fixes/run_test.sh"
