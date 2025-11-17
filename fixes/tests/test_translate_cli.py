import os
import shutil
import sys
from pathlib import Path

import pytest
from flask import Flask

from translation_cli import register

FIXTURES = Path(__file__).parent / "fixtures"
PO_FIXTURE = FIXTURES / "messages.po"


def _make_app(**config):
    app = Flask(__name__)
    app.config.update(SECRET_KEY="test-secret", **config)
    register(app)
    return app


def _prepare_lang(tmp_path, lang="es"):
    translations_dir = tmp_path / "translations"
    lang_dir = translations_dir / lang / "LC_MESSAGES"
    lang_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(PO_FIXTURE, lang_dir / "messages.po")
    return translations_dir


@pytest.mark.skipif(shutil.which("msgfmt") is None, reason="gettext msgfmt is required")
def test_cli_compile_success(tmp_path):
    translations_dir = _prepare_lang(tmp_path)
    output_dir = tmp_path / "compiled"
    app = _make_app(
        TRANSLATIONS_SOURCE_DIR=str(translations_dir),
        TRANSLATIONS_OUTPUT_DIR=str(output_dir),
    )

    runner = app.test_cli_runner()
    result = runner.invoke(args=["translate", "compile"])

    mo_path = output_dir / "es" / "LC_MESSAGES" / "messages.mo"
    assert result.exit_code == 0, result.output
    assert mo_path.exists()
    assert mo_path.stat().st_size > 0


def test_cli_reports_missing_msgfmt(tmp_path):
    translations_dir = _prepare_lang(tmp_path)
    output_dir = tmp_path / "compiled"
    fake_msgfmt = tmp_path / "missing" / "msgfmt.exe"
    app = _make_app(
        TRANSLATIONS_SOURCE_DIR=str(translations_dir),
        TRANSLATIONS_OUTPUT_DIR=str(output_dir),
        TRANSLATE_MSGFMT_PATH=str(fake_msgfmt),
    )

    runner = app.test_cli_runner()
    result = runner.invoke(args=["translate", "compile"])

    assert result.exit_code == 1
    assert "Configured msgfmt path" in result.output


def test_cli_reports_missing_translation_dir(tmp_path):
    translations_dir = tmp_path / "translations"
    output_dir = tmp_path / "compiled"
    app = _make_app(
        TRANSLATIONS_SOURCE_DIR=str(translations_dir),
        TRANSLATIONS_OUTPUT_DIR=str(output_dir),
        TRANSLATE_MSGFMT_PATH=sys.executable,
    )

    runner = app.test_cli_runner()
    result = runner.invoke(args=["translate", "compile"])

    assert result.exit_code == 1
    assert "does not exist" in result.output


@pytest.mark.skipif(os.name == "nt", reason="requires a POSIX /proc filesystem")
def test_cli_handles_unwritable_output_dir(tmp_path):
    translations_dir = _prepare_lang(tmp_path)
    output_dir = Path("/proc/translation-cli-tests")
    app = _make_app(
        TRANSLATIONS_SOURCE_DIR=str(translations_dir),
        TRANSLATIONS_OUTPUT_DIR=str(output_dir),
        TRANSLATE_MSGFMT_PATH=sys.executable,
    )

    runner = app.test_cli_runner()
    result = runner.invoke(args=["translate", "compile"])

    assert result.exit_code == 1
    assert "Cannot prepare output directory" in result.output


def test_compiler_raises_when_no_po_files(tmp_path):
    translations_dir = tmp_path / "translations"
    translations_dir.mkdir()
    app = _make_app(
        TRANSLATIONS_SOURCE_DIR=str(translations_dir),
        TRANSLATIONS_OUTPUT_DIR=str(tmp_path / "compiled"),
        TRANSLATE_MSGFMT_PATH=sys.executable,
    )

    runner = app.test_cli_runner()
    result = runner.invoke(args=["translate", "compile"])

    assert result.exit_code == 1
    assert "No '.po' files were found" in result.output
