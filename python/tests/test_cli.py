"""The ``django-bolt`` console script."""

from __future__ import annotations

import importlib.metadata
import importlib.util
import shutil
from pathlib import Path
from types import ModuleType

from click.testing import CliRunner

from django_bolt import cli


def _load_cli_as_installed(site_packages: Path) -> ModuleType:
    """Load a copy of ``cli.py`` from ``<site-packages>/django_bolt/cli.py``, where a wheel puts it.

    A wheel has no ``pyproject.toml``, so the copy has no repository files above it.
    """
    package_dir = site_packages / "django_bolt"
    package_dir.mkdir(parents=True)
    installed_cli = package_dir / "cli.py"
    shutil.copyfile(cli.__file__, installed_cli)
    spec = importlib.util.spec_from_file_location("installed_django_bolt_cli", installed_cli)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_version_prints_the_installed_distribution_version(tmp_path):
    installed_cli = _load_cli_as_installed(tmp_path / "site-packages")

    result = CliRunner().invoke(installed_cli.main, ["version"], catch_exceptions=False)

    assert result.exit_code == 0, result.output
    assert result.output == f"Django-Bolt version: {importlib.metadata.version('django-bolt')}\n"
