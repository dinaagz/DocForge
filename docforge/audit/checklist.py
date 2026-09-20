"""Checklist Engine — turn issues into a prioritized, actionable list.

Persists to `.docforge/checklists/current.json`. Each entry links back to
its issue id and declares the expected verification evidence.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ..events import emit, now_iso
from ..paths import DOCFORGE_DIR, ensure_layout
from .issues import load_issues

CHECKLIST_DIR = DOCFORGE_DIR / "checklists"
CURRENT_PATH = CHECKLIST_DIR / "current.json"

_SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


def _priority(issue: Dict[str, Any]) -> int:
    return _SEVERITY_ORDER.get(issue.get("severity", "LOW"), 4)


def build_from(issues: List[Dict[str, Any]]) -> Path:
    ensure_layout()
    CHECKLIST_DIR.mkdir(parents=True, exist_ok=True)
    tasks: List[Dict[str, Any]] = []
    for i, issue in enumerate(sorted(issues, key=_priority)):
        tid_base = issue.get("id", f"ISSUE-{i:04d}")
        tasks.append({
            "id": f"TASK-{tid_base}",
            "issue_id": tid_base,
            "priority": _priority(issue),
            "category": issue.get("category"),
            "severity": issue.get("severity"),
            "location": issue.get("location"),
            "action": issue.get("recommended_action")
                      or "investigate and correct",
            "dependencies": issue.get("dependencies", []),
            "owner": None,
            "status": "OPEN",
            "expected_evidence": "verifier passes without regression",
            "verification": None,
            "result": None,
        })
    doc = {
        "generated_at": now_iso(),
        "total": len(tasks),
        "tasks": tasks,
    }
    CURRENT_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2),
                            encoding="utf-8")
    emit("CHECKLIST_BUILT", tasks=len(tasks))
    return CURRENT_PATH


def build_from_registry() -> Path:
    return build_from(load_issues())


def load_current() -> Dict[str, Any]:
    if not CURRENT_PATH.exists():
        return {"tasks": [], "total": 0}
    return json.loads(CURRENT_PATH.read_text(encoding="utf-8"))
