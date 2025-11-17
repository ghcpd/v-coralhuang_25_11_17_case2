#!/usr/bin/env bash
set -euo pipefail
TAG=flask-translate-fix
docker build -f fixes/Dockerfile.fix -t ${TAG} .
# Run tests inside container
docker run --rm -v "$PWD":/app -w /app ${TAG} /bin/bash -lc \
  "python -m pip install -r fixes/requirements.txt && pytest -q"
