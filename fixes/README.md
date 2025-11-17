# Translation CLI hardening

This folder holds a drop-in replacement for `app/cli.py`, along with a fully
reproducible test environment that proves the translation workflow succeeds and
fails with informative errors on both Linux/macOS and Windows.

## Contents

- `src/translation_cli/`: hardened CLI implementation with platform-neutral
  msgfmt discovery, safe subprocess handling, and consistent directory logic.
- `tests/`: pytest suite (success path + failure modes) and a minimal
  `messages.po` fixture that is compiled during the happy-path test.
- `requirements.txt`: dependencies needed for the CLI and the tests.
- `setup.sh`, `run_test.sh`, `run_test.bat`: one-click environment bootstrap and
  execution on Linux/macOS or Windows.
- `run_in_docker.sh`, `Dockerfile`: reproducible Docker workflow that installs
  the gettext toolchain, sets up the venv, and runs the tests as a non-root user.
- `scripts/collect_logs.sh`: helper that captures stdout/stderr for any command
  and stores it under `artifacts/` (used by the test scripts).
- `scripts/cleanup.sh`: removes generated artifacts (and optionally the venv) so
  runs remain reproducible.
- `artifacts/`: location for pytest and CLI logs; `collect_logs.sh` always
  writes here so runs are auditable.
- `CHANGES.md`: detailed change log that documents every deliverable.

## Using the hardened CLI

1. Add `fixes/src` to your `PYTHONPATH` (the helper scripts already do this).
2. Import the new register helper in your Flask application:
   ```python
   from translation_cli import register
   register(app)
   ```
3. Optionally apply `fixes/patches/app_cli.patch` if you want to replace the
   original `app/cli.py` with the hardened implementation in place.

Configuration keys supported by the replacement CLI:

| Key | Default | Purpose |
| --- | --- | --- |
| `TRANSLATIONS_SOURCE_DIR` | `<app root>/translations` or `BABEL_TRANSLATION_DIRECTORY` | Where `.po` sources live |
| `TRANSLATIONS_OUTPUT_DIR` | `BABEL_TRANSLATION_DIRECTORY` or `TRANSLATIONS_SOURCE_DIR` | Target for `.mo` files |
| `TRANSLATE_MSGFMT_PATH` | auto-discovered via `MSGFMT_PATH` env var or `PATH` | Explicit msgfmt binary |
| `MSGFMT_PATH` (env) | see above | Alternate msgfmt path without editing config |

All filesystem inputs are resolved relative to the Flask app root if they are
not absolute paths. The compiler never shells out; it captures stdout/stderr and
raises actionable errors for missing gettext, missing translations, read-only
directories, and msgfmt failures.

## Local setup and tests

```bash
./fixes/setup.sh          # create .venv and install deps
./fixes/run_test.sh       # run pytest, logs -> fixes/artifacts/pytest.log
```

The Linux/macOS script ensures `PYTHONPATH` includes `fixes/src`. On Windows use
`fixes\run_test.bat` after creating the venv (with WSL or `py -m venv`).

The success test compiles `fixes/tests/fixtures/messages.po` with the real
`msgfmt` binary, asserts the `.mo` is > 0 bytes, and stores the log. Failure
tests cover missing gettext, missing translations, and permission problems.

If `msgfmt` is absent, install gettext (`sudo apt-get install gettext` on
Debian/Ubuntu, `brew install gettext` on macOS) or run inside Docker.

## Docker workflow

```bash
./fixes/run_in_docker.sh
```

The Dockerfile installs `gettext`, builds the venv, gives a non-root user write
access to `/workspace`, and runs `fixes/run_test.sh`. Provide extra commands to
`run_in_docker.sh` to override the default `pytest` invocation.

## Log collection and cleanup

- Capture command output: `./fixes/scripts/collect_logs.sh pytest-run ./fixes/run_test.sh`
- Reset artifacts (and optionally the venv): `./fixes/scripts/cleanup.sh [--venv]`

All logs live under `fixes/artifacts/` for easy review.
