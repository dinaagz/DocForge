"""Best-version tracking — baseline, current, previous, best, last_known_good.

State persists to `.docforge/scores/versions.json`. `submit(record)` keeps
the highest total unless a critical regression rejects the promotion.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from ..events import emit, now_iso
from ..paths import DOCFORGE_DIR, ensure_layout
from . import regression

VERSIONS_DIR = DOCFORGE_DIR / "scores"
VERSIONS_PATH = VERSIONS_DIR / "versions.json"


def _load() -> Dict[str, Any]:
    if not VERSIONS_PATH.exists():
        return {"baseline": None, "current": None, "previous": None,
                "best": None, "last_known_good": None, "history": []}
    return json.loads(VERSIONS_PATH.read_text(encoding="utf-8"))


def _save(state: Dict[str, Any]) -> None:
    ensure_layout()
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    VERSIONS_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2),
                             encoding="utf-8")


def reset() -> None:
    _save({"baseline": None, "current": None, "previous": None,
           "best": None, "last_known_good": None, "history": []})


def submit(record: Dict[str, Any]) -> Dict[str, Any]:
    """Register a new version record and update best/last-known-good."""
    state = _load()
    now = now_iso()
    rec = dict(record)
    rec.setdefault("ts", now)

    if state["baseline"] is None:
        state["baseline"] = rec

    state["previous"] = state["current"]
    state["current"] = rec
    state["history"].append(rec)

    best = state["best"]
    should_promote = True
    if best is not None:
        reg = regression.check(best, rec)
        if reg["blocking"]:
            should_promote = False
        elif float(rec.get("total", 0) or 0) <= float(best.get("total", 0) or 0):
            should_promote = False
    if should_promote:
        state["best"] = rec
        state["last_known_good"] = rec
        emit("VERSION_PROMOTED", total=rec.get("total"))
    else:
        emit("VERSION_KEPT", best_total=(state["best"] or {}).get("total"),
             new_total=rec.get("total"))
    _save(state)
    return state


def best() -> Optional[Dict[str, Any]]:
    return _load().get("best")


def state() -> Dict[str, Any]:
    return _load()
