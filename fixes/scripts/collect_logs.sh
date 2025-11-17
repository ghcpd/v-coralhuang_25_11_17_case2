#!/usr/bin/env bash
set -euo pipefail
mkdir -p fixes/artifacts
# Save env and installed packages for audit
python -V > fixes/artifacts/python_version.txt
pip freeze > fixes/artifacts/pip_freeze.txt || true
pytest -q || true
