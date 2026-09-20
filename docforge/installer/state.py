"""Installer state — installed versions + migration ledger.

Files:
- `<state_dir>/installed.json`   : list of installed versions with paths.
- `<state_dir>/migrations.json`  : applied migration ids.
- `<state_dir>/config.json`      : channel, auto-update flag.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import layout


def _state_dir() -> Path:
    env = os.environ.get("DOCFORGE_STATE_DIR")
    d = Path(env) if env else layout.state_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d


def _load(name: str, default: Any) -> Any:
    p = _state_dir() / f"{name}.json"
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def _save(name: str, data: Any) -> None:
    p = _state_dir() / f"{name}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{name}.", suffix=".json",
                               dir=str(p.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, p)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# ── versions ─────────────────────────────────────────────────

def installed_versions() -> Dict[str, Dict[str, Any]]:
    d = _load("installed", {"versions": {}, "current": None})
    return d.get("versions", {})


def current_version() -> Optional[str]:
    return _load("installed", {"versions": {}, "current": None}).get("current")


def record_installed(version: str, path: str) -> None:
    d = _load("installed", {"versions": {}, "current": None})
    d["versions"][version] = {"path": str(path), "installed": True}
    d["current"] = version
    _save("installed", d)


def forget_installed(version: str) -> None:
    d = _load("installed", {"versions": {}, "current": None})
    d.get("versions", {}).pop(version, None)
    if d.get("current") == version:
        remaining = list(d.get("versions", {}))
        d["current"] = remaining[-1] if remaining else None
    _save("installed", d)


def set_current(version: str) -> None:
    d = _load("installed", {"versions": {}, "current": None})
    if version not in d.get("versions", {}):
        raise KeyError(f"version {version} is not installed")
    d["current"] = version
    _save("installed", d)


def reset_versions() -> None:
    _save("installed", {"versions": {}, "current": None})


# ── migrations ───────────────────────────────────────────────

def applied_migrations() -> List[str]:
    return list(_load("migrations", {"applied": []}).get("applied", []))


def mark_migration(mig_id: str) -> None:
    d = _load("migrations", {"applied": []})
    if mig_id not in d["applied"]:
        d["applied"].append(mig_id)
        _save("migrations", d)


def reset_migrations() -> None:
    _save("migrations", {"applied": []})


# ── config ───────────────────────────────────────────────────

def get_config() -> Dict[str, Any]:
    return _load("config", {"channel": "stable", "auto_update": False})


def set_config(**kwargs: Any) -> Dict[str, Any]:
    d = get_config()
    d.update(kwargs)
    _save("config", d)
    return d
