"""Evidence Store — append-only JSONL, indexed by gate/task."""
from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..events import emit, now_iso
from ..paths import DOCFORGE_DIR, ensure_layout

COMPLETION_DIR = DOCFORGE_DIR / "completion"
EVIDENCE_PATH = COMPLETION_DIR / "evidence.jsonl"


def _ensure_dir() -> None:
    ensure_layout()
    COMPLETION_DIR.mkdir(parents=True, exist_ok=True)


def record(gate: str, source: str, result: str,
           artifact: Optional[str] = None,
           task: Optional[str] = None,
           test: Optional[str] = None,
           location: Optional[Dict[str, Any]] = None,
           conclusion: Optional[str] = None,
           **extra: Any) -> Dict[str, Any]:
    _ensure_dir()
    entry: Dict[str, Any] = {
        "id": f"E-{uuid.uuid4().hex[:10]}",
        "ts": now_iso(),
        "gate": gate,
        "source": source,
        "result": result,
        "task": task,
        "test": test,
        "artifact": artifact,
        "location": location or {},
        "conclusion": conclusion or "",
    }
    if artifact and Path(artifact).exists():
        entry["hash"] = _hash_file(Path(artifact))
    if extra:
        entry["extra"] = extra
    with open(EVIDENCE_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    emit("EVIDENCE_RECORDED", gate=gate, source=source, result=result)
    return entry


def _hash_file(p: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(p, "rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()[:16]


def _iter() -> List[Dict[str, Any]]:
    if not EVIDENCE_PATH.exists():
        return []
    out: List[Dict[str, Any]] = []
    for line in EVIDENCE_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def for_gate(gate: str) -> List[Dict[str, Any]]:
    return [e for e in _iter() if e.get("gate") == gate]


def all_gates_with_evidence() -> List[str]:
    return sorted({e.get("gate") for e in _iter() if e.get("gate")})


def reset() -> None:
    if EVIDENCE_PATH.exists():
        EVIDENCE_PATH.unlink()
