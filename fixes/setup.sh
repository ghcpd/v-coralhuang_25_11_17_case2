#!/bin/bash
# Setup script for Linux/macOS
# Creates and activates virtual environment, installs dependencies
# Usage: ./setup.sh or bash setup.sh

set -e

echo "=== Microblog Translation CLI - Setup ==="
echo

# Check if we're in the fixes directory
if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found. Run this script from the fixes/ directory."
    exit 1
fi

# Create virtual environment
echo "[1/2] Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "[2/2] Activating virtual environment and installing dependencies..."
source .venv/bin/activate
pip install -q -r requirements.txt

echo
echo "✓ Setup complete!"
echo
echo "To activate the virtual environment in future terminal sessions:"
echo "  source .venv/bin/activate"
echo
echo "To run tests:"
echo "  ./run_test.sh"
echo
