#!/usr/bin/env python3
"""Executable shim so `./docforge_cli.py` and `docforge` both work."""
from __future__ import annotations

import sys

from docforge.cli import main


if __name__ == "__main__":
    sys.exit(main())
