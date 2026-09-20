"""Roll back to a previously installed version."""
from __future__ import annotations

from typing import List, Optional

from . import layout, state


def list_versions() -> List[str]:
    versions = list(state.installed_versions().keys())
    return sorted(versions)


def can_rollback() -> bool:
    vs = list_versions()
    return len(vs) >= 2


def previous_version() -> Optional[str]:
    vs = list_versions()
    cur = state.current_version()
    others = [v for v in vs if v != cur]
    return others[-1] if others else None


def rollback(to: Optional[str] = None) -> dict:
    target = to or previous_version()
    if not target:
        return {"ok": False, "error": "no previous version to roll back to"}
    if target not in state.installed_versions():
        return {"ok": False, "error": f"version {target} not installed"}
    path = state.installed_versions()[target]["path"]
    layout.current_pointer().write_text(path, encoding="utf-8")
    state.set_current(target)
    return {"ok": True, "current": target, "path": path}
