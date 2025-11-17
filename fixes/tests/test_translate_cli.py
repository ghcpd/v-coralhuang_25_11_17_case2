import shutil
import sys
from pathlib import Path

import pytest
from flask import Flask

from fixes.translate_cli import register

FIXTURE_PO = Path(__file__).with_name("fixtures") / "messages.po"


def _make_app(tmp_path, **overrides):
    app = Flask(__name__)
    translations_dir = tmp_path / "translations"
    app.config["TRANSLATIONS_INPUT_DIRECTORY"] = translations_dir
    app.config["BABEL_TRANSLATION_DIRECTORY"] = tmp_path / "compiled"
    app.config.update(overrides)
    register(app)
    return app


def _write_fixture(tmp_path, locale="fr") -> None:
    target_dir = tmp_path / "translations" / locale / "LC_MESSAGES"
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(FIXTURE_PO, target_dir / "messages.po")


def _run_compile(app):
    runner = app.test_cli_runner()
    return runner.invoke(args=["translate", "compile"])


def _assert_cli_message(result, fragment):
    template = str(result.exception) if result.exception else result.output
    assert fragment in template


def test_translate_compile_success(tmp_path):
    _write_fixture(tmp_path)
    msgfmt = shutil.which("msgfmt")
    if not msgfmt:
        pytest.skip(
            "msgfmt not available in PATH; install the GNU gettext toolchain to run this test."
        )
    app = _make_app(tmp_path, BABEL_MSGFMT_PATH=msgfmt)
    result = _run_compile(app)

    assert result.exit_code == 0, result.output
    mo_file = tmp_path / "compiled" / "fr" / "LC_MESSAGES" / "messages.mo"
    assert mo_file.exists()
    assert mo_file.stat().st_size > 0


def test_translate_compile_missing_msgfmt(tmp_path):
    _write_fixture(tmp_path)
    missing = tmp_path / "missing-msgfmt"
    app = _make_app(tmp_path, BABEL_MSGFMT_PATH=missing)
    result = _run_compile(app)

    assert result.exit_code != 0
    _assert_cli_message(result, "Configured msgfmt")


@pytest.mark.skipif(sys.platform.startswith("win"), reason="chmod behavior varies on Windows")
def test_translate_compile_permission_error(tmp_path):
    _write_fixture(tmp_path)
    app = _make_app(tmp_path)
    if not shutil.which("msgfmt"):
        pytest.skip(
            "msgfmt is required for the permission error test; install gettext to continue."
        )
    compiled_dir = tmp_path / "compiled"
    compiled_dir.mkdir(parents=True, exist_ok=True)
    compiled_dir.chmod(0o555)
    try:
        result = _run_compile(app)
        assert result.exit_code != 0
        _assert_cli_message(result, "Permission denied")
    finally:
        compiled_dir.chmod(0o755)
