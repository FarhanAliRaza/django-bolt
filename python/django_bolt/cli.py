import tomllib
from pathlib import Path

import click


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main():
    """Django-Bolt command line interface."""


@main.command()
def version():
    """Show Django-Bolt version."""
    cli_dir = Path(__file__).parent.resolve()
    toml_file = cli_dir / "../../pyproject.toml"

    with toml_file.open("rb") as f:
        pyproject = tomllib.load(f)

    click.echo(f"Django-Bolt version: {pyproject['project']['version']}")
