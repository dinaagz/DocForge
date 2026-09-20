"""Uninstall — removes the runtime, preserves every user artifact."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict

from . import layout


def plan_uninstall() -> Dict[str, Any]:
    """Report what would be removed without touching disk."""
    root = layout.runtime_root()
    remove = [str(root / "versions"), str(root / "venv"),
              str(root / "cache"), str(layout.bin_dir() / "docforge"),
              str(layout.bin_dir() / "docforge.cmd")]
    return {
        "runtime_root": str(root),
        "remove": remove,
        "keep_state": str(layout.state_dir()),
        "user_data_preserved": ["<project>/input", "<project>/output",
                                 "<project>/work", "<project>/.docforge"],
    }


def uninstall(purge_state: bool = False) -> Dict[str, Any]:
    """Remove runtime binaries and installed versions. Never touches
    user project directories. Set `purge_state=True` to also remove the
    runtime state (installed versions ledger, config).
    """
    removed = []
    root = layout.runtime_root()
    for sub in ("versions", "venv", "cache"):
        p = root / sub
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)
            removed.append(str(p))
    for name in ("docforge", "docforge.cmd"):
        b = layout.bin_dir() / name
        if b.exists() or b.is_symlink():
            try:
                b.unlink()
                removed.append(str(b))
            except OSError:
                pass
    if purge_state:
        s = layout.state_dir()
        if s.exists():
            shutil.rmtree(s, ignore_errors=True)
            removed.append(str(s))
    return {"ok": True, "removed": removed}
