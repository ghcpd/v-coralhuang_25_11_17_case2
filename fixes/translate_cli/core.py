from dataclasses import dataclass
from pathlib import Path
import os
import shutil
import subprocess
from typing import Iterable, List


class TranslationError(Exception):
    """Represents an issue that prevents translation compilation."""


@dataclass
class TranslationSettings:
    translations_dir: Path
    output_dir: Path
    msgfmt_path: Path


class TranslateCompiler:
    """Compiles .po catalogs into .mo files using msgfmt."""

    def __init__(self, settings: TranslationSettings) -> None:
        self.settings = settings

    def compile(self) -> List[Path]:
        """Compile every .po file found under the translations directory."""
        translations_dir = self.settings.translations_dir
        if not translations_dir.exists():
            raise TranslationError(
                f"Translations directory '{translations_dir}' is missing."
            )
        if not translations_dir.is_dir():
            raise TranslationError(
                f"Translations path '{translations_dir}' is not a directory."
            )

        po_files = list(self._find_po_files(translations_dir))
        if not po_files:
            raise TranslationError(
                f"No '.po' files were discovered under '{translations_dir}'."
            )

        compiled_files: List[Path] = []
        for po_file in po_files:
            lang = self._detect_language(po_file)
            mo_file = self._mo_target(po_file, lang)
            mo_file.parent.mkdir(parents=True, exist_ok=True)
            try:
                self._invoke_msgfmt(po_file, mo_file)
                compiled_files.append(mo_file)
            except FileNotFoundError as exc:
                raise TranslationError(
                    f"msgfmt executable '{self.settings.msgfmt_path}' could not be run: {exc}"
                )
            except PermissionError as exc:
                raise TranslationError(
                    f"Permission denied when writing '{mo_file}': {exc}"
                )
            except subprocess.CalledProcessError as exc:
                stderr = exc.stderr.strip() if exc.stderr else ""
                raise TranslationError(
                    f"msgfmt failed compiling '{po_file}': {stderr or exc}"
                )
        return compiled_files

    def _find_po_files(self, base: Path) -> Iterable[Path]:
        for root, _, files in os.walk(base):
            for filename in sorted(files):
                if filename.endswith(".po"):
                    yield Path(root) / filename

    def _detect_language(self, po_path: Path) -> str:
        relative = po_path.relative_to(self.settings.translations_dir)
        if relative.parts:
            return relative.parts[0]
        return "unknown"

    def _mo_target(self, po_path: Path, lang: str) -> Path:
        return (
            self.settings.output_dir
            / lang
            / "LC_MESSAGES"
            / f"{po_path.stem}.mo"
        )

    def _invoke_msgfmt(self, po_file: Path, mo_file: Path) -> None:
        cmd = [str(self.settings.msgfmt_path), "-o", str(mo_file), str(po_file)]
        subprocess.run(cmd, check=True, capture_output=True, text=True)


def _normalize_directory(value, root: Path, default: Path) -> Path:
    if value:
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = root / candidate
        return candidate
    return default


def _resolve_msgfmt(config: dict, root: Path) -> Path:
    override = config.get("BABEL_MSGFMT_PATH") or config.get("MSGFMT_PATH")
    if override:
        candidate = Path(override)
        if not candidate.is_absolute():
            candidate = root / candidate
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate
        fallback = shutil.which(override)
        if fallback:
            return Path(fallback)
        raise TranslationError(
            f"Configured msgfmt '{override}' is not available or not executable."
        )
    resolved = shutil.which("msgfmt")
    if resolved:
        return Path(resolved)
    raise TranslationError(
        "msgfmt executable not found on PATH; install the GNU gettext toolchain."
    )


def build_translation_settings(app) -> TranslationSettings:
    root = Path(app.root_path)
    default_translations_dir = root / "translations"
    translations_dir = _normalize_directory(
        app.config.get("TRANSLATIONS_INPUT_DIRECTORY"), root, default_translations_dir
    )
    default_output_dir = translations_dir
    output_dir = _normalize_directory(
        app.config.get("BABEL_TRANSLATION_DIRECTORY"), root, default_output_dir
    )
    msgfmt_path = _resolve_msgfmt(app.config, root)
    return TranslationSettings(translations_dir=translations_dir, output_dir=output_dir, msgfmt_path=msgfmt_path)
