"""
Comprehensive tests for translation CLI.

Tests cover:
- Success case: valid .po file is compiled to .mo
- Missing msgfmt dependency
- Missing translations directory
- No .po files in directory
- Permission errors on write
"""
import os
import sys
import stat
import tempfile
import shutil
import unittest
import subprocess
from io import StringIO
from pathlib import Path
from unittest import mock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db, cli
from config import Config


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"


class TranslateCompileSuccessTest(unittest.TestCase):
    """Test successful translation compilation."""

    def setUp(self):
        """Set up test environment."""
        self.app = create_app(TestConfig)
        cli.register(self.app)  # Register CLI commands
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.runner = self.app.test_cli_runner()

        # Create temporary translations directory with fixture
        self.temp_dir = tempfile.mkdtemp()
        self.translations_dir = os.path.join(self.temp_dir, "translations")
        os.makedirs(os.path.join(self.translations_dir, "de"), exist_ok=True)

        # Copy fixture .po file
        fixture_po = Path(__file__).parent / "fixtures" / "messages.po"
        dest_po = os.path.join(self.translations_dir, "de", "messages.po")
        if fixture_po.exists():
            shutil.copy(str(fixture_po), dest_po)
        else:
            # Create minimal .po file if fixture not found
            with open(dest_po, "w", encoding="utf-8") as f:
                f.write(
                    """# Translation file
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\\n"
"Language: de\\n"

msgid "Hello"
msgstr "Hallo"
"""
                )

        # Patch app to use temp translations directory
        self.app.config["BABEL_TRANSLATION_DIRECTORY"] = self.translations_dir

    def tearDown(self):
        """Clean up test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compile_success_creates_mo_file(self):
        """Test that translate compile creates .mo file."""
        # Mock subprocess.run to simulate successful msgfmt execution
        def mock_run(cmd, **kwargs):
            """Mock msgfmt execution that creates .mo file."""
            # Parse command line to find output file
            if "-o" in cmd:
                idx = cmd.index("-o")
                mo_file = cmd[idx + 1]
                # Create a minimal .mo file
                os.makedirs(os.path.dirname(mo_file), exist_ok=True)
                with open(mo_file, "wb") as f:
                    f.write(b"\xde\x12\x04\x95")  # Magic number for .mo file
            # Return success result
            result = subprocess.CompletedProcess(cmd, 0, "", "")
            return result
        
        # Mock both shutil.which and subprocess.run
        with mock.patch("app.cli.subprocess.run", side_effect=mock_run):
            with mock.patch("app.cli.shutil.which", return_value="/usr/bin/msgfmt"):
                result = self.runner.invoke(args=["translate", "compile"])
        
        self.assertEqual(result.exit_code, 0, f"Output: {result.output}")

        # Verify .mo file was created
        mo_file = os.path.join(self.translations_dir, "de", "messages.mo")
        self.assertTrue(os.path.isfile(mo_file), f".mo file not found: {mo_file}")

        # Verify .mo file is non-empty
        mo_size = os.path.getsize(mo_file)
        self.assertGreater(mo_size, 0, f".mo file is empty: {mo_file}")

    def test_compile_success_output_message(self):
        """Test that successful compile produces clear output."""
        # Mock subprocess.run to simulate successful msgfmt execution
        def mock_run(cmd, **kwargs):
            """Mock msgfmt execution that creates .mo file."""
            if "-o" in cmd:
                idx = cmd.index("-o")
                mo_file = cmd[idx + 1]
                os.makedirs(os.path.dirname(mo_file), exist_ok=True)
                with open(mo_file, "wb") as f:
                    f.write(b"\xde\x12\x04\x95")
            result = subprocess.CompletedProcess(cmd, 0, "", "")
            return result
        
        with mock.patch("app.cli.subprocess.run", side_effect=mock_run):
            with mock.patch("app.cli.shutil.which", return_value="/usr/bin/msgfmt"):
                result = self.runner.invoke(args=["translate", "compile"])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Successfully compiled", result.output)


class TranslateCompileMissingMsgfmtTest(unittest.TestCase):
    """Test error handling when msgfmt is missing."""

    def setUp(self):
        """Set up test environment."""
        self.app = create_app(TestConfig)
        cli.register(self.app)  # Register CLI commands
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.runner = self.app.test_cli_runner()

        # Create temporary translations directory
        self.temp_dir = tempfile.mkdtemp()
        self.translations_dir = os.path.join(self.temp_dir, "translations")
        os.makedirs(os.path.join(self.translations_dir, "de"), exist_ok=True)

        # Create a minimal .po file
        po_file = os.path.join(self.translations_dir, "de", "messages.po")
        with open(po_file, "w", encoding="utf-8") as f:
            f.write('msgid ""\nmsgstr ""\n\nmsgid "test"\nmsgstr "test"\n')

        self.app.config["BABEL_TRANSLATION_DIRECTORY"] = self.translations_dir

        # Override msgfmt path to non-existent location
        self.app.config["MSGFMT_PATH"] = "/nonexistent/msgfmt"

    def tearDown(self):
        """Clean up test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compile_missing_msgfmt_returns_error(self):
        """Test that missing msgfmt returns non-zero exit code."""
        result = self.runner.invoke(args=["translate", "compile"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("msgfmt not found", result.output)


class TranslateCompileMissingTranslationsDirTest(unittest.TestCase):
    """Test error handling when translations directory is missing."""

    def setUp(self):
        """Set up test environment."""
        self.app = create_app(TestConfig)
        cli.register(self.app)  # Register CLI commands
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.runner = self.app.test_cli_runner()

        # Set translations directory to non-existent location
        self.temp_dir = tempfile.mkdtemp()
        nonexistent_dir = os.path.join(self.temp_dir, "nonexistent")
        self.app.config["BABEL_TRANSLATION_DIRECTORY"] = nonexistent_dir

    def tearDown(self):
        """Clean up test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compile_missing_translations_dir_returns_error(self):
        """Test that missing translations directory returns non-zero exit code."""
        result = self.runner.invoke(args=["translate", "compile"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("not found", result.output)


class TranslateCompileNoPOFilesTest(unittest.TestCase):
    """Test error handling when no .po files are found."""

    def setUp(self):
        """Set up test environment."""
        self.app = create_app(TestConfig)
        cli.register(self.app)  # Register CLI commands
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.runner = self.app.test_cli_runner()

        # Create empty translations directory
        self.temp_dir = tempfile.mkdtemp()
        self.translations_dir = os.path.join(self.temp_dir, "translations")
        os.makedirs(self.translations_dir, exist_ok=True)

        self.app.config["BABEL_TRANSLATION_DIRECTORY"] = self.translations_dir

    def tearDown(self):
        """Clean up test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compile_no_po_files_returns_error(self):
        """Test that no .po files returns non-zero exit code."""
        # Mock shutil.which to bypass msgfmt check
        with mock.patch("app.cli.shutil.which", return_value="/usr/bin/msgfmt"):
            result = self.runner.invoke(args=["translate", "compile"])
        
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("No .po files found", result.output)


class TranslateCompilePermissionErrorTest(unittest.TestCase):
    """Test error handling when write permission is denied."""

    def setUp(self):
        """Set up test environment."""
        self.app = create_app(TestConfig)
        cli.register(self.app)  # Register CLI commands
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.runner = self.app.test_cli_runner()

        # Create temporary translations directory
        self.temp_dir = tempfile.mkdtemp()
        self.translations_dir = os.path.join(self.temp_dir, "translations")
        self.lang_dir = os.path.join(self.translations_dir, "de")
        os.makedirs(self.lang_dir, exist_ok=True)

        # Create a minimal .po file
        po_file = os.path.join(self.lang_dir, "messages.po")
        with open(po_file, "w", encoding="utf-8") as f:
            f.write('msgid ""\nmsgstr ""\n\nmsgid "test"\nmsgstr "test"\n')

        self.app.config["BABEL_TRANSLATION_DIRECTORY"] = self.translations_dir

        # Remove write permissions on language directory
        os.chmod(self.lang_dir, stat.S_IRUSR | stat.S_IXUSR)  # read and execute only

    def tearDown(self):
        """Clean up test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        # Restore write permissions before cleanup
        try:
            os.chmod(
                self.lang_dir, stat.S_IRWXU
            )  # restore read, write, execute for owner
        except (FileNotFoundError, OSError):
            pass

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compile_permission_error_returns_error(self):
        """Test that permission error returns non-zero exit code."""
        result = self.runner.invoke(args=["translate", "compile"])
        self.assertNotEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
