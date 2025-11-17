import os
import shutil
import stat
import sys
import tempfile
import subprocess
import pytest
from flask import Flask
import sys, os
# allow tests to import a helper config module from fixes/ for the example app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'fixes')))
from app import create_app

from fixes.translation_cli import register


def write_minimal_po(path):
    with open(path, "w", encoding="utf-8") as f:
        f.write('''msgid ""
msgstr ""
"Language: en\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
\nmsgid "Hello"
msgstr "Hello translated\n"''')


@pytest.fixture
def app(tmp_path):
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite://"

    app = create_app(TestConfig)
    # Ensure our fixed CLI is used instead of the original
    # Remove any existing 'translate' command
    if "translate" in app.cli.commands:
        del app.cli.commands["translate"]
    register(app)
    return app


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def find_msgfmt_binary():
    return shutil.which("msgfmt")


def test_compile_success(tmp_path, app, runner):
    # Skip if msgfmt not installed locally; this test is meant for environments with msgfmt (e.g. Docker)
    msgfmt = find_msgfmt_binary()
    if not msgfmt:
        pytest.skip("msgfmt not present in PATH; skipping success compilation test")

    src = tmp_path / "translations"
    langdir = src / "en" / "LC_MESSAGES"
    langdir.mkdir(parents=True)
    po_file = langdir / "messages.po"
    write_minimal_po(po_file)

    out = tmp_path / "out"
    app.config["BABEL_TRANSLATION_DIRECTORY"] = str(out)

    # call the CLI
    result = runner.invoke(args=["translate", "compile", "--translations-dir", str(src)])
    assert result.exit_code == 0
    # verify mo exists
    mo_path = out / "en" / "LC_MESSAGES" / "messages.mo"
    assert mo_path.exists() and mo_path.stat().st_size > 0


def test_compile_missing_msgfmt(tmp_path, app, runner):
    src = tmp_path / "translations"
    langdir = src / "en" / "LC_MESSAGES"
    langdir.mkdir(parents=True)
    po_file = langdir / "messages.po"
    write_minimal_po(po_file)

    app.config["MSGFMT_CMD"] = "/nonexistent/msgfmt"

    result = runner.invoke(args=["translate", "compile", "--translations-dir", str(src)])
    assert result.exit_code == 3
    assert "msgfmt executable not found" in result.output


@pytest.mark.skipif(sys.platform.startswith("win"), reason="POSIX perms required")
def test_compile_no_write_permission(tmp_path, app, runner):
    msgfmt = find_msgfmt_binary()
    if not msgfmt:
        pytest.skip("msgfmt not present in PATH; skipping permission test")

    src = tmp_path / "translations"
    langdir = src / "en" / "LC_MESSAGES"
    langdir.mkdir(parents=True)
    po_file = langdir / "messages.po"
    write_minimal_po(po_file)

    out = tmp_path / "out"
    out.mkdir(parents=True)

    # Make output dir unwritable
    os.chmod(out, stat.S_IREAD)

    app = runner._test_ctx.application
    app.config["BABEL_TRANSLATION_DIRECTORY"] = str(out)

    result = runner.invoke(args=["translate", "compile", "--translations-dir", str(src)])
    assert result.exit_code == 4
    assert "Permission denied writing" in result.output


def test_no_po_files(tmp_path, runner):
    src = tmp_path / "translations"
    src.mkdir(parents=True)

    result = runner.invoke(args=["translate", "compile", "--translations-dir", str(src)])
    assert result.exit_code == 6
    assert "No .po files found" in result.output
