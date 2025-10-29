"""Development-time type stub generation for Django-Bolt.

This package inspects Django models and emits .pyi stubs into a local
"stubs/" directory for editor/CI type checkers (Pyright, ty).

Usage (via CLI):
    uv run django-bolt types sync
    uv run django-bolt types watch
"""

from .inspector import collect_model_metadata
from .emit import emit_model_stubs

__all__ = [
    "collect_model_metadata",
    "emit_model_stubs",
]




