"""Application configuration."""
import os


class Config:
    """Base configuration."""

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///microblog.db"
    )
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    LANGUAGES = {"en": "English", "de": "Deutsch"}

    # Translation configuration
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_TRANSLATION_DIRECTORY = None  # Use default (translations/)
    # MSGFMT_PATH can be set to override msgfmt detection
