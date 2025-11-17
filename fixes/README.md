# Fixes for Cross-platform translation CLI and Tests

This directory contains a set of fixes and test harness for the translations CLI to ensure cross-platform compatibility and reproducibility.

Quick start (Linux/macOS):

1) Setup a virtualenv and install dependencies:

   ./fixes/setup.sh

2) Run tests:

   ./fixes/run_test.sh

Windows:

1) run fixes\run_test.bat

Docker:

1) ./fixes/run_in_docker.sh

What changed:

- `fixes/translation_cli.py`: robust, cross-platform CLI with resolved msgfmt and safe subprocess invocation. To use: register it into your app by importing register and calling register(app) or via `fixes/register_cli.py`.
- `fixes/tests/`: pytest tests covering success and failure scenarios.
- `fixes/Dockerfile.fix`: installs gettext and ensures writable translation output dir for non-root user.
- `fixes/run_test.sh`, `fixes/run_test.bat`, `fixes/run_in_docker.sh`: one-click scripts to run tests.

Notes:
- The tests try to use a system-installed `msgfmt`. If not present locally, tests that rely on it will be skipped, but Docker will install `gettext`.
- To run the improved CLI manually in your environment, call:

  python -c "from app import create_app; from fixes.translation_cli import register; app = create_app(); register(app); app.cli()"

  Or run `python fixes/register_cli.py` to register the improved CLI and run the app.

- All original application source files are left untouched.
