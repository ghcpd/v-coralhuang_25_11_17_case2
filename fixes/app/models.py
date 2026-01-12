"""Database models."""
from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """User model."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), index=True, unique=True)


class Post(db.Model):
    """Post model."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
