#!/usr/bin/env bash
set -euo pipefail
. .venv/bin/activate
mkdir -p fixes/artifacts
pytest -q --maxfail=1 2>&1 | tee fixes/artifacts/pytest_output.txt
rc=${PIPESTATUS[0]:-0}
exit $rc
