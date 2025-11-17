#!/usr/bin/env bash
set -euo pipefail
# Remove compiled .mo files
find . -path "*/LC_MESSAGES/messages.mo" -delete || true
rm -rf fixes/artifacts || true
mkdir -p fixes/artifacts
