from flask import current_app
import click

from .core import TranslateCompiler, TranslationError, build_translation_settings


def register(app):
    @app.cli.group()
    def translate():
        """Manage translations via gettext."""
        pass

    @translate.command()
    def init():
        """Create new translations (not yet implemented)."""
        click.echo("Translation initialization is handled outside this helper.")

    @translate.command()
    def update():
        """Update existing catalogs (not yet implemented)."""
        click.echo("Translation updates are managed separately from this helper.")

    @translate.command(name="compile")
    def compile_command() -> None:
        """Compile all available .po files into .mo binaries."""
        ctx = click.get_current_context()
        settings = build_translation_settings(current_app)
        compiler = TranslateCompiler(settings)
        try:
            compiled = compiler.compile()
        except TranslationError as exc:
            ctx.fail(str(exc))
        click.echo(f"Compiled {len(compiled)} translation file(s).")
        click.echo(f"Mo files written under '{settings.output_dir}'.")
