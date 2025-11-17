#!/bin/bash
# Docker test runner script
# Builds Docker image and runs tests inside container
# Usage: ./run_in_docker.sh or bash run_in_docker.sh

set -e

echo "=== Microblog Translation CLI - Docker Test Run ==="
echo

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH"
    exit 1
fi

# Check if we're in the fixes directory
if [ ! -f "Dockerfile.fix" ]; then
    echo "ERROR: Dockerfile.fix not found. Run this script from the fixes/ directory."
    exit 1
fi

IMAGE_NAME="microblog-fix"
CONTAINER_NAME="microblog-fix-test-$$"

echo "[1/4] Building Docker image..."
docker build -f Dockerfile.fix -t $IMAGE_NAME . > /dev/null 2>&1

echo "[2/4] Creating test fixture directory inside container..."
docker run --rm \
    -v "$(pwd)/translations:/app/translations" \
    $IMAGE_NAME \
    mkdir -p /app/translations/de 2>/dev/null || true

echo "[3/4] Preparing test translations..."
mkdir -p translations/de 2>/dev/null || true
if [ ! -f "translations/de/messages.po" ]; then
    mkdir -p translations/de
    cp tests/fixtures/messages.po translations/de/messages.po 2>/dev/null || \
    cat > translations/de/messages.po << 'EOF'
# Translation catalogue for German language
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\n"
"Language: de\n"

msgid "Hello"
msgstr "Hallo"

msgid "Goodbye"
msgstr "Auf Wiedersehen"

msgid "Please log in to access this page."
msgstr "Bitte melden Sie sich an, um auf diese Seite zuzugreifen."
EOF
fi

echo "[4/4] Running tests in container..."
docker run --rm \
    -v "$(pwd):/app" \
    $IMAGE_NAME \
    python -m pytest tests/test_translate_cli.py -v --tb=short 2>&1 | tee artifacts/docker_test_output.log

TEST_EXIT=$?

echo
echo "=== Docker Test Run Complete ==="
if [ $TEST_EXIT -eq 0 ]; then
    echo "✓ All tests passed"
else
    echo "✗ Tests failed with exit code: $TEST_EXIT"
fi

exit $TEST_EXIT
