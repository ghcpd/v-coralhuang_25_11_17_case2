# Helper to register the improved CLI into an existing Flask app for manual usage
from app import create_app
from fixes.translation_cli import register


def register_into_app(app=None):
    if app is None:
        app = create_app()
    # Remove existing 'translate' command to avoid conflicts
    if "translate" in app.cli.commands:
        del app.cli.commands["translate"]
    register(app)
    return app


if __name__ == "__main__":
    app = register_into_app()
    app.run()
