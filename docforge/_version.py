"""Single source of truth for the DocForge version.

Any file that needs the version imports it from here. Do NOT duplicate.
"""
from __future__ import annotations

VERSION: str = "0.2.0"
API_COMPATIBLE: str = "0.2"  # backward-compatible minor line
