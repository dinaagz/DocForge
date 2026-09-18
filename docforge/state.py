"""Persistent, atomic JSON state store — the source of truth.

Never trust conversation memory. Read state, decide, write state.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict

from .paths import STATE_DIR, ensure_layout


class Store:
    def __init__(self, base: Path = STATE_DIR) -> None:
        self.base = base
        ensure_layout()

    def _path(self, name: str) -> Path:
        return self.base / f"{name}.json"

    def load(self, name: str, default: Dict[str, Any] | None = None) -> Dict[str, Any]:
        p = self._path(name)
        if not p.exists():
            return dict(default) if default else {}
        with open(p, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def save(self, name: str, data: Dict[str, Any]) -> None:
        p = self._path(name)
        p.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=f".{name}.", suffix=".json", dir=str(p.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
            os.replace(tmp, p)
        except Exception:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise

    def update(self, name: str, **fields: Any) -> Dict[str, Any]:
        d = self.load(name)
        d.update(fields)
        self.save(name, d)
        return d


# Convenient default store
store = Store()
