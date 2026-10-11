"""Settings of the example project, with the database and static root in a temporary directory.

The benchmarks seed and read users. They must not change the database of the
example project. conftest.py sets BOLT_BENCH_DIR before Django reads this module.
"""

from __future__ import annotations

import os
from pathlib import Path

from testproject.settings import *  # noqa: F403

_BENCH_DIR = Path(os.environ["BOLT_BENCH_DIR"])

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": _BENCH_DIR / "db.sqlite3"}}
STATIC_ROOT = _BENCH_DIR / "staticfiles"
