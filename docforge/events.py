"""Append-only event log — full traceability."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from .paths import EVENTS_LOG, ensure_layout


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def emit(event: str, **fields: Any) -> None:
    ensure_layout()
    entry = {"ts": now_iso(), "event": event, **fields}
    with open(EVENTS_LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
