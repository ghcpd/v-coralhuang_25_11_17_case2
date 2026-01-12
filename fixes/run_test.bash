#!/bin/bash
# Windows test runner script (run from fixes directory)
# Usage: bash run_test.bash or ./run_test.bash

set -e

echo "=== Microblog Translation CLI - Windows Test Run ==="
echo

# Check if we're in the fixes directory
if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found. Run this script from the fixes/ directory."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "[1/4] Creating virtual environment..."
    python -m venv .venv
else
    echo "[1/4] Virtual environment already exists"
fi

# Activate virtual environment
echo "[2/4] Activating virtual environment..."
source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate

# Install dependencies
echo "[3/4] Installing dependencies..."
pip install -q -r requirements.txt

# Run tests with coverage
echo "[4/4] Running tests..."
python -m pytest tests/test_translate_cli.py -v --tb=short 2>&1 | tee artifacts/test_output.log

# Capture exit code
TEST_EXIT=$?

echo
echo "=== Test Run Complete ==="
if [ $TEST_EXIT -eq 0 ]; then
    echo "✓ All tests passed"
else
    echo "✗ Tests failed with exit code: $TEST_EXIT"
fi

exit $TEST_EXIT
