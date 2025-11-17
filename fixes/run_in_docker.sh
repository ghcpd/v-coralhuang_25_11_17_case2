#!/usr/bin/env bash
set -euo pipefail
IMAGE=fixes_test_image:latest

docker build -f fixes/Dockerfile.fix -t $IMAGE .

docker run --rm -v "$(pwd)":/app $IMAGE /bin/bash -c "python -m venv .venv && . .venv/bin/activate && pip install -r fixes/requirements.txt && pytest -q --maxfail=1 || exit $?"
