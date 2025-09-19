import os
import sys
import click

from .bootstrap import ensure_django_ready
from .api import BoltAPI


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main():
    """Django-Bolt command line."""


@main.command()
@click.option("--host", default="0.0.0.0", show_default=True)
@click.option("--port", default=8000, type=int, show_default=True)
def run(host: str, port: int):
    """Run the Django-Bolt server in embedded/attached mode."""
    info = ensure_django_ready()
    click.echo(f"[django-bolt] Django setup: mode={info.get('mode')} debug={info.get('debug')}")
    click.echo(f"[django-bolt] DB: {info.get('database')} name={info.get('database_name')}")

    api = BoltAPI()

    # In the future, we can import user-defined routes via env or module path.
    # For now, serve an empty API to exercise the stack.
    click.echo(f"[django-bolt] Listening on http://{host}:{port}")
    api.serve(host, port)


@main.command()
def migrations():
    """Show unapplied migrations (attached/embedded)."""
    ensure_django_ready()
    from django.core.management import call_command

    call_command("showmigrations", list=True)


@main.command()
def migrate():
    """Apply migrations (attached/embedded)."""
    ensure_django_ready()
    from django.core.management import call_command

    call_command("migrate", interactive=False, run_syncdb=True)


@main.command()
@click.argument("app_label", required=False)
@click.option("--name", default=None, help="Name of the migration")
@click.option("--empty", is_flag=True, default=False, help="Create an empty migration")
def makemigrations(app_label: str | None, name: str | None, empty: bool):
    """Create new migrations for apps (attached/embedded)."""
    ensure_django_ready()
    from django.core.management import call_command

    kwargs = {}
    if name:
        kwargs["name"] = name
    if empty:
        kwargs["empty"] = True

    if app_label:
        call_command("makemigrations", app_label, **kwargs)
    else:
        call_command("makemigrations", **kwargs)


