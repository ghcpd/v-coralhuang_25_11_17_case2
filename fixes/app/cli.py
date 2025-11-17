"""
Translation CLI for Microblog application.

Provides cross-platform, robust translation compilation with:
- Dynamic msgfmt detection from PATH or configuration
- Clear error messages for missing dependencies
- Platform-agnostic subprocess execution
- Configurable translation directories
"""
import os
import subprocess
import sys
import shutil
import click
from flask import current_app


def get_app_root(app_instance):
    """Get the application root directory."""
    return os.path.abspath(os.path.dirname(app_instance.instance_path))


def find_msgfmt():
    """
    Find msgfmt executable.

    Returns:
        str: Path to msgfmt executable.

    Raises:
        click.ClickException: If msgfmt is not found.
    """
    # First, check if msgfmt_path is explicitly configured
    msgfmt_path = current_app.config.get("MSGFMT_PATH")
    if msgfmt_path and os.path.isfile(msgfmt_path):
        return msgfmt_path

    # Try to find msgfmt in PATH
    msgfmt_exe = "msgfmt.exe" if sys.platform == "win32" else "msgfmt"
    found = shutil.which(msgfmt_exe)
    if found:
        return found

    # Provide helpful error message
    if sys.platform == "win32":
        error_msg = (
            "msgfmt not found in PATH. Please install gettext for Windows:\n"
            "  - Download from: https://gnuwin32.sourceforge.io/packages/gettext.htm\n"
            "  - Or configure MSGFMT_PATH in app config\n"
            "  - Or install via: choco install gettext-binary (if using Chocolatey)"
        )
    else:
        error_msg = (
            "msgfmt not found in PATH. Please install gettext:\n"
            "  - Ubuntu/Debian: sudo apt-get install gettext\n"
            "  - macOS: brew install gettext\n"
            "  - Or configure MSGFMT_PATH in app config"
        )
    raise click.ClickException(error_msg)


def register(app):
    """
    Register translation CLI commands with Flask app.

    Args:
        app: Flask application instance.
    """

    @app.cli.group()
    def translate():
        """Manage translations."""
        pass

    @translate.command()
    @click.argument("lang")
    def init(lang):
        """Initialize a new language for translation."""
        # Not implemented for this fix
        pass

    @translate.command()
    def update():
        """Update translation files."""
        # Not implemented for this fix
        pass

    @translate.command()
    def compile():
        """Compile .po files to .mo files.

        Raises:
            click.ClickException: On msgfmt not found, missing translations dir,
                                or no .po files.
        """
        try:
            # Find msgfmt executable
            msgfmt_path = find_msgfmt()

            # Determine translations directory
            app_root = get_app_root(app)
            translations_dir = os.path.join(app_root, "translations")

            # Allow override via config
            translations_dir = current_app.config.get(
                "BABEL_TRANSLATION_DIRECTORY", translations_dir
            )

            # Validate translations directory exists
            if not os.path.isdir(translations_dir):
                raise click.ClickException(
                    f"Translations directory not found: {translations_dir}\n"
                    f"Expected structure:\n"
                    f"  {translations_dir}/\n"
                    f"    de/\n"
                    f"      LC_MESSAGES/\n"
                    f"        messages.po"
                )

            # Collect all .po files
            po_files = []
            for dirname, _, files in os.walk(translations_dir):
                for filename in files:
                    if filename.endswith(".po"):
                        po_files.append(
                            {
                                "po_path": os.path.join(dirname, filename),
                                "lang_dir": dirname,
                            }
                        )

            if not po_files:
                raise click.ClickException(
                    f"No .po files found in: {translations_dir}\n"
                    f"Expected .po files in language subdirectories."
                )

            # Compile each .po file
            errors = []
            for po_info in po_files:
                po_file = po_info["po_path"]
                lang_dir = po_info["lang_dir"]

                # Output .mo file in same directory as .po
                mo_file = os.path.join(lang_dir, "messages.mo")

                try:
                    # Ensure directory exists
                    os.makedirs(lang_dir, exist_ok=True)

                    # Use argument list instead of shell=True
                    cmd = [msgfmt_path, "-o", mo_file, po_file]

                    result = subprocess.run(
                        cmd, capture_output=True, text=True, check=False
                    )

                    if result.returncode != 0:
                        errors.append(
                            f"Failed to compile {po_file}:\n"
                            f"  stdout: {result.stdout}\n"
                            f"  stderr: {result.stderr}"
                        )
                    else:
                        # Verify .mo file was created and is non-empty
                        if not os.path.isfile(mo_file) or os.path.getsize(mo_file) == 0:
                            errors.append(
                                f"Compiled .mo file is empty or missing: {mo_file}"
                            )
                        else:
                            click.echo(f"Compiled: {po_file} -> {mo_file}")

                except (FileNotFoundError, PermissionError) as e:
                    errors.append(f"Error processing {po_file}: {e}")

            if errors:
                error_text = "\n".join(errors)
                raise click.ClickException(
                    f"Translation compilation failed:\n{error_text}"
                )

            click.echo(f"Successfully compiled {len(po_files)} translation file(s).")

        except click.ClickException:
            raise
        except Exception as e:
            raise click.ClickException(f"Unexpected error during compilation: {e}")
