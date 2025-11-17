# Translation CLI Fixes

This directory holds the reproducible fix for the `translate` CLI without touching the original files. Everything lives under `fixes/` so you can run, inspect, and copy the updated logic at will.

## Highlights
- `fixes/translate_cli/` contains the improved, cross-platform CLI module with configurable msgfmt discovery, robust subprocess handling, and clear diagnostics about missing `.po` files or permissions failures.
- `fixes/tests/` includes pytest suites that exercise success, missing `msgfmt`, and permission-denied scenarios using a minimal `messages.po` fixture.
- All new scripts, Docker assets, logs, and documentation live under this tree so the baseline repository stays untouched.

## Local setup & verification (macOS/Linux)
1. `cd fixes` and run `./setup.sh` (creates `.venv`, upgrades pip, installs requirements).
2. Still under `fixes`, execute `./run_test.sh`. The script activates `.venv` and runs `pytest tests`, returning the same exit status.
3. To collect execution evidence, run `./scripts/collect_logs.sh`; it replays the test run and stores stdout/stderr under `fixes/artifacts/tests.log`.

> On Linux, the success test requires a working `msgfmt` binary. The script skips the success case and surfaces a clear message if gettext is missing.

## Windows workflow
1. Create a virtual environment (e.g., `python -m venv .venv`) from the `fixes` directory and install dependencies with `.\.venv\Scripts\pip.exe install -r requirements.txt`.
2. Run `fixes\run_test.bat` to activate the venv, execute pytest, and propagate the exit code.
3. Logs can be collected manually by redirecting `run_test.bat` output into `artifacts\tests.log` or using PowerShell wrappers.

## Docker support
1. `./run_in_docker.sh` (from the repo root) builds `fixes/Dockerfile.fix` into an image named `flask-translate-fix`, installs gettext, creates a non-root user, and installs Python dependencies.
2. The same script runs the tests inside the container, ensuring reproducible `msgfmt` availability and writing artifacts to `fixes/artifacts/` via a bind mount.
3. The provided `Dockerfile.fix` can be reused for manual experimentation or as a base for `docker-compose` if needed.

## Adopting the fix into the application
- Apply `fixes/patches/fix_translate_cli.patch` (it rewrites `app/cli.py` to the new implementation) or copy `fixes/translate_cli/` into your application and register `register(app)` as before. The patch shows exactly how to replace the old CLI while keeping the same `register()` API.
- Configure the following settings if needed:
  - `TRANSLATIONS_INPUT_DIRECTORY`: Optional path (relative to app root) to the `.po` files (`translations` by default).
  - `BABEL_TRANSLATION_DIRECTORY`: Optional output directory (`TRANSLATIONS_INPUT_DIRECTORY` by default).
  - `BABEL_MSGFMT_PATH` / `MSGFMT_PATH`: Optional path to the `msgfmt` binary; otherwise it is resolved via `shutil.which`.

## Logs & artifacts
- `fixes/scripts/collect_logs.sh` runs the tests and captures stdout/stderr under `fixes/artifacts/tests.log` for auditing.
- `fixes/artifacts/` is the designated drop zone for log files, generated `.mo` files during manual runs, or test outputs.

## Additional Notes
- All CLI commands still register through the `register(app)` pattern, keeping compatibility with the `create_app()` factory and `app.cli` registration.
- When migrating, copy the `fixes/translate_cli/` package into your source tree (or adjust the import paths) and re-run your existing `flask translate compile` flow.
