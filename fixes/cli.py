import os
import click
from flask import current_app
from .translate_helper import compile_translations, TranslationCompileError


def register(app):
    @app.cli.group()
    def translate():
        "Translation utilities"
        pass

    @translate.command(name="compile")
    @click.option('--translations-dir', default=None, help='Directory with translations')
    @click.option('--output-dir', default=None, help='Output directory for compiled .mo')
    @click.option('--msgfmt', default=None, help='Path to msgfmt executable to use')
    @click.option('--verbose', is_flag=True, default=False)
    def compile_cmd(translations_dir, output_dir, msgfmt, verbose):
        "Compile translations to .mo using msgfmt found in PATH or provided path"
        basedir = os.path.abspath(os.path.dirname(__file__))
        default_translations = os.path.join(basedir, 'translations')
        translations_dir = translations_dir or current_app.config.get('BABEL_TRANSLATION_DIRECTORY', default_translations)
        output_dir = output_dir or translations_dir

        try:
            compile_translations(translations_dir, output_dir=output_dir, msgfmt_path=msgfmt, verbose=verbose)
        except TranslationCompileError as e:
            click.echo(str(e), err=True)
            raise SystemExit(2)
        except Exception as e:
            click.echo(f"Unexpected error: {e}", err=True)
            raise SystemExit(3)
        else:
            click.echo("Translations compiled successfully")
