## Translation CLI hardening

- Added a standalone, drop-in CLI implementation under `fixes/src/translation_cli`
  that discovers `msgfmt` cross-platform, validates translation directories, and
  reports actionable errors for missing gettext, empty catalogs, and
  permission issues while avoiding `shell=True`.
- Introduced pytest coverage (success + three failure modes) that exercises the
  CLI via Flask's `test_cli_runner` and compiles a real `.po` fixture into
  `.mo`, asserting the compiled file exists and is non-empty.
- Created reproducible tooling: `requirements.txt`, `setup.sh`, `run_test.sh`,
  `run_test.bat`, Dockerfile + `run_in_docker.sh`, log collectors, and cleanup
  scripts with artifacts stored under `fixes/artifacts/`.
- Documented the workflow via `README.md` and provided `scripts/collect_logs.sh`
  plus `scripts/cleanup.sh` for repeatable execution.
