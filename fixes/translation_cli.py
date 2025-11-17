import os
import shutil
import subprocess
import click
import sys
from flask import current_app


def find_msgfmt(configured=None):
    """
    Resolve a msgfmt executable path.
    1) If configured (string), validate it exists and is executable.
    2) Try to resolve in PATH using shutil.which("msgfmt").
    Returns absolute path or None.
    """
    if configured:
        if os.path.isabs(configured) and os.path.isfile(configured):
            return configured
        # Try to resolve a bare name
        which = shutil.which(configured)
        if which:
            return which
        return None
    # Look up in PATH
    return shutil.which("msgfmt")


def compile_po_to_mo(msgfmt_cmd, po_file, mo_file):
    """Compile one .po into .mo using msgfmt subprocess. Use list args for safety."""
    cmd = [msgfmt_cmd, "-o", mo_file, po_file]
    # Ensure parent dir exists
    os.makedirs(os.path.dirname(mo_file), exist_ok=True)
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as e:
        raise
    except PermissionError as e:
        raise
    except subprocess.CalledProcessError as e:
        raise


def register(app, group_name="translate"):  # preserve signature for drop-in
    @app.cli.group(name=group_name)
    def translate():
        """Translation tools (improved cross-platform and robust)."""
        pass

    @translate.command(name="compile")
    @click.option("--translations-dir", default=None,
                  help="Directory where .po files live; defaults to app.root_path/translations")
    def compile(translations_dir):
        # Determine translation source and output
        src = translations_dir or current_app.config.get(
            "TRANSLATIONS_DIR",
            os.path.join(current_app.root_path, "translations"),
        )
        out = current_app.config.get("BABEL_TRANSLATION_DIRECTORY", src)

        if not os.path.isdir(src):
            click.echo(f"Translations directory not found: {src}")
            sys.exit(2)

        # Walk translations dir and collect .po files
        po_files = []
        for dirname, _, files in os.walk(src):
            for filename in files:
                if not filename.endswith(".po"):
                    continue
                po_files.append((dirname, filename))

        if not po_files:
            click.echo(f"No .po files found under {src}")
            sys.exit(6)

        # Find msgfmt
        configured_msgfmt = current_app.config.get("MSGFMT_CMD")
        msgfmt_cmd = find_msgfmt(configured_msgfmt)
        if not msgfmt_cmd:
            click.echo("msgfmt executable not found; please install gettext or set MSGFMT_CMD in config")
            sys.exit(3)

        # Compile
        for dirname, filename in po_files:
            lang = os.path.basename(os.path.dirname(dirname))
            po_file = os.path.join(dirname, filename)
            mo_file = os.path.join(out, lang, "LC_MESSAGES", "messages.mo")
            try:
                compile_po_to_mo(msgfmt_cmd, po_file, mo_file)
                click.echo(f"Compiled {po_file} -> {mo_file}")
            except FileNotFoundError:
                click.echo(f"msgfmt executable not found: {msgfmt_cmd}")
                sys.exit(3)
            except PermissionError:
                click.echo(f"Permission denied writing: {mo_file}")
                sys.exit(4)
            except subprocess.CalledProcessError as e:
                click.echo(f"msgfmt failed: {e}")
                sys.exit(5)

        click.echo("Translations compiled successfully")
        return 0

        click.echo("Translations compiled successfully")
        return 0

    return translate
