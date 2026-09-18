"""Persistent memory — decisions, hypotheses, corrections, rationale.

Answers questions like "why was this modification made?" and
"which agent made it?".
"""
from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List

from .events import emit, now_iso
from .paths import MEMORY_DIR, ensure_layout


def _mem_path(kind: str):
    ensure_layout()
    return MEMORY_DIR / f"{kind}.jsonl"


def record(kind: str, **fields: Any) -> Dict[str, Any]:
    """Append a structured memory entry and return it."""
    entry = {"id": uuid.uuid4().hex[:12], "ts": now_iso(), "kind": kind, **fields}
    with open(_mem_path(kind), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    emit("MEMORY_RECORDED", kind=kind, mid=entry["id"])
    return entry


def read(kind: str) -> List[Dict[str, Any]]:
    p = _mem_path(kind)
    if not p.exists():
        return []
    out: List[Dict[str, Any]] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def decision(topic: str, choice: str, rationale: str, agent: str = "planner", **extra: Any) -> Dict[str, Any]:
    return record("decisions", topic=topic, choice=choice, rationale=rationale, agent=agent, **extra)


def correction(target: str, before: str, after: str, agent: str, rationale: str = "", **extra: Any) -> Dict[str, Any]:
    return record("corrections", target=target, before=before, after=after,
                  agent=agent, rationale=rationale, **extra)


def hypothesis(text: str, source: str, confidence: str = "medium") -> Dict[str, Any]:
    return record("hypotheses", text=text, source=source, confidence=confidence)


def why(target: str) -> List[Dict[str, Any]]:
    """Return every memory entry referencing a target — full audit trail."""
    all_kinds = ("decisions", "corrections", "hypotheses")
    hits: List[Dict[str, Any]] = []
    for k in all_kinds:
        for entry in read(k):
            if target in json.dumps(entry, ensure_ascii=False):
                hits.append(entry)
    return hits
