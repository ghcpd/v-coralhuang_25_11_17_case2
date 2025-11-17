#!/usr/bin/env bash
set -euo pipefail
mkdir -p fixes/artifacts
pytest -q fixes/tests/test_translate_compile.py --junitxml=fixes/artifacts/tests-results.xml || true
# copy any compiled mo files for inspection
find fixes -type f -name "*.mo" -exec cp --parents {} fixes/artifacts/ \; || true
