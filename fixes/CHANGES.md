# Changes

- Added a standalone translation CLI implementation under `fixes/translate_cli/` that discovers `msgfmt`, resolves configurable directories relative to the Flask app, and reports clear errors for missing catalogs or permission issues.
- Introduced pytest-based coverage (`fixes/tests/`) including success, missing dependency, and permission-denied scenarios backed by a minimal `messages.po` fixture.
- Provided reproducible tooling (`setup.sh`, `run_test.*`, Dockerfile, README, and log collectors) so the fixes can be validated locally, on Windows, and inside containers without altering the baseline repository.
