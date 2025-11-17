"""Microblog application entry point."""
from app import create_app, db, cli
from app.models import User, Post
from config import Config

app = create_app(Config)
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    """Shell context for Flask CLI."""
    return {"db": db, "User": User, "Post": Post}


if __name__ == "__main__":
    app.run()
