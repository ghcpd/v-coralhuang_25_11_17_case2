import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

import click
from flask import current_app


class TranslationCompileError(RuntimeError):
    """Raised when the translation compile workflow cannot complete."""


@dataclass
class TranslationPaths:
    source_dir: Path
    output_dir: Path

    def resolve_mo_path(self, po_path: Path) -> Path:
        """Return the .mo path for a given .po file."""
        lang_dir = po_path.parents[1].name  # <lang>/LC_MESSAGES/file.po
        return self.output_dir / lang_dir / "LC_MESSAGES" / f"{po_path.stem}.mo"


def register(app):
    """Register the fixed translate CLI commands with the Flask app."""

    @app.cli.group("translate")
    def translate():
        """Translation management commands."""

    @translate.command("compile")
    def compile_translations():
        """Compile all *.po files into *.mo catalogs."""
        try:
            compiler = TranslationCompiler.from_app(current_app)
            compiled = compiler.compile_all()
        except TranslationCompileError as exc:
            click.secho(str(exc), fg="red")
            raise SystemExit(1) from exc

        if not compiled:
            click.secho(
                "No translations were compiled. "
                "Make sure *.po files exist under the configured directory.",
                fg="yellow",
            )
            return

        click.secho(f"Compiled {len(compiled)} translation catalog(s):", fg="green")
        for mo_path in compiled:
            click.echo(f" - {mo_path}")


class TranslationCompiler:
    """Encapsulates the translation compile logic so it can be unit tested."""

    def __init__(self, root: Path, paths: TranslationPaths, msgfmt: str):
        self.root = root
        self.paths = paths
        self.msgfmt = msgfmt

    @classmethod
    def from_app(cls, app):
        root = Path(app.root_path)
        paths = cls._resolve_paths(app, root)
        msgfmt = cls._resolve_msgfmt(app.config)
        return cls(root=root, paths=paths, msgfmt=msgfmt)

    @staticmethod
    def _resolve_paths(app, root: Path) -> TranslationPaths:
        source_dir = _resolve_directory(
            root=root,
            configured=app.config.get("TRANSLATIONS_SOURCE_DIR")
            or app.config.get("BABEL_TRANSLATION_DIRECTORY"),
            default=root / "translations",
        )
        output_dir = _resolve_directory(
            root=root,
            configured=app.config.get("TRANSLATIONS_OUTPUT_DIR")
            or app.config.get("BABEL_TRANSLATION_DIRECTORY")
            or app.config.get("TRANSLATIONS_SOURCE_DIR"),
            default=source_dir,
        )
        return TranslationPaths(source_dir=source_dir, output_dir=output_dir)

    @staticmethod
    def _resolve_msgfmt(config) -> str:
        configured_candidates: Sequence[str] = [
            config.get("TRANSLATE_MSGFMT_PATH") or "",
            os.environ.get("MSGFMT_PATH") or "",
        ]
        for candidate in configured_candidates:
            if not candidate:
                continue
            resolved = _resolve_msgfmt_candidate(candidate)
            if resolved:
                return resolved
            raise TranslationCompileError(
                f"Configured msgfmt path '{candidate}' is not executable."
            )

        auto_detected = shutil.which("msgfmt")
        if auto_detected:
            return auto_detected

        raise TranslationCompileError(
            "msgfmt executable could not be found. "
            "Set TRANSLATE_MSGFMT_PATH or MSGFMT_PATH to point at a gettext "
            "installation."
        )

    def compile_all(self) -> List[Path]:
        source_dir = self.paths.source_dir
        if not source_dir.exists():
            raise TranslationCompileError(
                f"Translations directory '{source_dir}' does not exist."
            )
        po_files = sorted(source_dir.glob("*/LC_MESSAGES/*.po"))
        if not po_files:
            raise TranslationCompileError(
                f"No '.po' files were found under '{source_dir}'."
            )

        compiled: List[Path] = []
        for po_path in po_files:
            mo_path = self.paths.resolve_mo_path(po_path)
            try:
                mo_path.parent.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                raise TranslationCompileError(
                    f"Cannot prepare output directory '{mo_path.parent}': {exc}"
                ) from exc

            self._run_msgfmt(po_path, mo_path)
            compiled.append(mo_path)
        return compiled

    def _run_msgfmt(self, po_path: Path, mo_path: Path) -> None:
        cmd = [self.msgfmt, "-o", str(mo_path), str(po_path)]
        try:
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise TranslationCompileError(
                f"msgfmt executable '{self.msgfmt}' was not found."
            ) from exc
        except PermissionError as exc:
            raise TranslationCompileError(
                f"Permission denied while executing '{self.msgfmt}': {exc}"
            ) from exc
        except subprocess.CalledProcessError as exc:
            stdout = exc.stdout.strip() if exc.stdout else ""
            stderr = exc.stderr.strip() if exc.stderr else ""
            details = "\n".join(
                line for line in (stdout, stderr) if line
            ) or "msgfmt exited with a non-zero status."
            raise TranslationCompileError(
                f"msgfmt failed for '{po_path}': {details}"
            ) from exc


def _resolve_directory(root: Path, configured: str, default: Path) -> Path:
    if configured:
        configured_path = Path(configured)
        if not configured_path.is_absolute():
            configured_path = root / configured_path
        return configured_path
    return default


def _looks_like_path(candidate: str) -> bool:
    sep = os.sep
    alt = os.altsep
    return sep in candidate or (alt and alt in candidate)


def _resolve_msgfmt_candidate(candidate: str) -> str:
    expanded = os.path.expanduser(candidate)
    path_candidate = Path(expanded)
    if path_candidate.is_absolute() or _looks_like_path(candidate):
        resolved_path = path_candidate
        if not resolved_path.is_absolute():
            resolved_path = Path.cwd() / resolved_path
        if resolved_path.is_file() and os.access(resolved_path, os.X_OK):
            return str(resolved_path)
        return ""
    resolved = shutil.which(candidate)
    return resolved or ""
