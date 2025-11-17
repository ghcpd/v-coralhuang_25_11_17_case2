#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
IMAGE_NAME="translate-cli-fixed"

docker build -f "$ROOT_DIR/Dockerfile" -t "$IMAGE_NAME" "$ROOT_DIR/.."

if [[ $# -gt 0 ]]; then
  docker run --rm -t "$IMAGE_NAME" "$@"
else
  docker run --rm -t "$IMAGE_NAME"
fi
