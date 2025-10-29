from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

import click

from . import collect_model_metadata, emit_model_stubs


def _ensure_django() -> None:
    """Ensure Django app registry is ready.

    - Adds CWD to sys.path to resolve local project modules
    - Calls django.setup() when apps registry isn't ready
    - Surfaces setup errors to the caller for easier debugging
    """
    # Ensure current working directory is importable
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    import django
    from django.apps import apps

    if not apps.ready:
        if "DJANGO_SETTINGS_MODULE" not in os.environ:
            raise RuntimeError(
                "DJANGO_SETTINGS_MODULE is not set. Export it, e.g. DJANGO_SETTINGS_MODULE=testproject.settings"
            )
        # Let exceptions propagate if setup fails
        django.setup()


@click.group()
def types() -> None:
    """Dev-time type stub commands."""


@types.command()
@click.option("--stubs-dir", default="stubs", show_default=True, help="Directory to write .pyi stubs into")
@click.option("--overlay", is_flag=True, help="Write .pyi next to source modules for maximum Pyright precedence")
def sync(stubs_dir: str, overlay: bool) -> None:
    """Generate model .pyi stubs once."""
    _ensure_django()
    out = Path(stubs_dir)
    out.mkdir(parents=True, exist_ok=True)

    models = collect_model_metadata()
    emit_model_stubs(models, out, overlay=overlay)
    loc = "source tree (overlay)" if overlay else str(out)
    click.echo(f"✓ Wrote stubs for {len(models)} models to {loc}")


@types.command()
@click.option("--stubs-dir", default="stubs", show_default=True, help="Directory to write .pyi stubs into")
@click.option("--overlay", is_flag=True, help="Write .pyi next to source modules for maximum Pyright precedence")
def watch(stubs_dir: str, overlay: bool) -> None:
    """Watch for changes and re-generate stubs."""
    try:
        from watchfiles import run_process
    except Exception:  # pragma: no cover - optional dep
        click.echo("watchfiles is not installed. Run: uv add watchfiles")
        return

    _ensure_django()
    out = Path(stubs_dir)
    out.mkdir(parents=True, exist_ok=True)

    def _generate() -> None:
        models = collect_model_metadata()
        emit_model_stubs(models, out, overlay=overlay)
        loc = "source tree (overlay)" if overlay else str(out)
        click.echo(f"✓ Wrote stubs for {len(models)} models to {loc}")

    def _target() -> None:  # function signature for run_process
        _generate()

    # Watch common Django app locations
    watch_paths = [
        "**/models.py",
        "**/models/*.py",
    ]
    click.echo("Watching for changes… Press Ctrl+C to stop.")
    run_process(".", target=_target, watch_filter=lambda p: any(p.endswith(s) for s in ["models.py"]))


