from __future__ import annotations

import importlib.metadata

import click


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main():
    """Django-Bolt command line interface."""


@main.command()
def version():
    """Show Django-Bolt version."""
    click.echo(f"Django-Bolt version: {importlib.metadata.version('django-bolt')}")
