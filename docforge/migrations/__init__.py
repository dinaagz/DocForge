"""Versioned, idempotent migrations for internal schemas/state.

Each migration is a module `NNN_name.py` exposing:
- `ID` : stable string id (e.g. "001_initial")
- `DESCRIPTION` : one-line description
- `apply()` : callable performing the migration; must be idempotent.
"""
from __future__ import annotations

import importlib
import pkgutil
from typing import Any, Dict, List


def registry() -> List[Dict[str, Any]]:
    """Discover all migrations in this package, ordered by id."""
    out: List[Dict[str, Any]] = []
    package = __name__
    for _, name, ispkg in pkgutil.iter_modules(__path__):
        if ispkg or name.startswith("_"):
            continue
        mod = importlib.import_module(f"{package}.{name}")
        mid = getattr(mod, "ID", name)
        out.append({"id": mid,
                    "description": getattr(mod, "DESCRIPTION", ""),
                    "apply": getattr(mod, "apply", None)})
    out.sort(key=lambda m: m["id"])
    return out


def run_pending() -> List[str]:
    """Apply every migration not yet in the state ledger. Returns ids."""
    from ..installer import state
    applied = set(state.applied_migrations())
    ran: List[str] = []
    for mig in registry():
        if mig["id"] in applied:
            continue
        fn = mig["apply"]
        if callable(fn):
            fn()
        state.mark_migration(mig["id"])
        ran.append(mig["id"])
    return ran
