# CHANGES

- Added `fixes/translation_cli.py`: improved translations compile command with cross-platform resolution for `msgfmt`, robust subprocess calls, and clear error handling.
- Added pytest tests in `fixes/tests` covering success, missing msgfmt, no write permissions, and no .po files.
- Added a reproducible `fixes/Dockerfile.fix` that installs `gettext` and runs tests as an unprivileged user.
- Added helper scripts for setup, running tests, and collecting logs.
- No original files were modified; `microblog.py` remains the same and continues to use `app.cli.register(app)`. Tests register the improved CLI for verification.
