#!/usr/bin/env bash
set -euo pipefail
TMPDIR=$(mktemp -d)
# Create translations dir
mkdir -p "$TMPDIR/translations/en/LC_MESSAGES"
cat > "$TMPDIR/translations/en/LC_MESSAGES/messages.po" <<'PO'
msgid ""
msgstr ""
"Language: en\n"
"Content-Type: text/plain; charset=UTF-8\n"

msgid "Hello"
msgstr "Hello translated\n"
PO

python - <<PY
from app import create_app
from fixes.translation_cli import register
app = create_app()
# override config
app.config['BABEL_TRANSLATION_DIRECTORY'] = r"$TMPDIR/out"
if 'translate' in app.cli.commands:
    del app.cli.commands['translate']
register(app)
with app.test_cli_runner().isolated_filesystem():
    res = app.test_cli_runner().invoke(['translate','compile','--translations-dir',r"$TMPDIR/translations"])
    print('EXIT:', res.exit_code)
    print(res.output)
PY
