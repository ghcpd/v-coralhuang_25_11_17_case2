"""
Cross-platform translation CLI that can be dropped into the microblog app.

This module keeps the same ``register(app)`` entry point that the original
microblog CLI expects, but the implementation lives under ``fixes/`` so the
baseline repository is untouched.
"""

from .cli import (
    TranslationCompileError,
    TranslationCompiler,
    register,
)

__all__ = ["TranslationCompiler", "TranslationCompileError", "register"]
