import os
import shutil
import subprocess
from typing import Optional


def find_msgfmt(configured_path: Optional[str] = None) -> Optional[str]:
    """Return the path to msgfmt if available, or None."""
    if configured_path:
        if os.path.isfile(configured_path) and os.access(configured_path, os.X_OK):
            return configured_path
        return None

    # Try PATH
    path = shutil.which("msgfmt")
    if path:
        return path

    # On Windows, try common install locations
    if os.name == "nt":
        candidates = [
            r"C:\Program Files\gettext\bin\msgfmt.exe",
            r"C:\Program Files (x86)\gettext\bin\msgfmt.exe",
        ]
        for c in candidates:
            if os.path.isfile(c) and os.access(c, os.X_OK):
                return c

    return None


class TranslationCompileError(RuntimeError):
    pass


def compile_translations(
    translations_dir: str,
    output_dir: Optional[str] = None,
    msgfmt_path: Optional[str] = None,
    verbose: bool = False,
) -> None:
    """Compile .po files into .mo files.

    Raises TranslationCompileError on failures.
    """
    translations_dir = os.path.abspath(translations_dir)

    if not os.path.isdir(translations_dir):
        raise TranslationCompileError(
            f"Translations directory not found: {translations_dir}"
        )

    if output_dir is None:
        output_dir = translations_dir

    output_dir = os.path.abspath(output_dir)

    msgfmt = find_msgfmt(msgfmt_path)
    if not msgfmt:
        raise TranslationCompileError(
            "msgfmt not found. Install gettext or configure MSGFMT_PATH."
        )

    any_po = False
    for root, _, files in os.walk(translations_dir):
        for fname in files:
            if not fname.endswith(".po"):
                continue
            any_po = True
            po_path = os.path.join(root, fname)
            rel_lang = os.path.relpath(root, translations_dir).split(os.sep)[0]
            mo_dir = os.path.join(output_dir, rel_lang, "LC_MESSAGES")
            os.makedirs(mo_dir, exist_ok=True)
            mo_path = os.path.join(mo_dir, "messages.mo")

            cmd = [msgfmt, "-o", mo_path, po_path]

            try:
                proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
            except FileNotFoundError as exc:
                raise TranslationCompileError(
                    f"msgfmt executable not found at '{msgfmt}'" + str(exc)
                )
            except PermissionError as exc:
                raise TranslationCompileError(
                    f"Permission error while running msgfmt: {exc}"
                )

            if proc.returncode != 0:
                err = proc.stderr.strip() or proc.stdout.strip()
                raise TranslationCompileError(
                    f"msgfmt failed (returncode={proc.returncode}): {err}"
                )

            if verbose:
                print(f"Compiled {po_path} -> {mo_path}")

    if not any_po:
        raise TranslationCompileError("No .po files found in translations directory")
