"""Issue Registry — each anomaly is a structured, persistent object."""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..events import emit, now_iso
from ..paths import DOCFORGE_DIR, ensure_layout

AUDIT_DIR = DOCFORGE_DIR / "audits"
ISSUES_PATH = AUDIT_DIR / "issues.jsonl"

SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW")
STATUSES = ("OPEN", "IN_PROGRESS", "RESOLVED", "BLOCKED", "WAIVED")


@dataclass
class Issue:
    id: str
    category: str
    severity: str
    location: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    impact: str = ""
    recommended_action: str = ""
    dependencies: List[str] = field(default_factory=list)
    status: str = "OPEN"
    verification: Dict[str, Any] = field(default_factory=dict)
    created_by: str = "audit-engine"
    resolved_by: Optional[str] = None
    created_at: str = ""

    @classmethod
    def new(cls, category: str, severity: str, description: str,
            location: Optional[Dict[str, Any]] = None,
            **extra: Any) -> "Issue":
        if severity not in SEVERITIES:
            raise ValueError(f"invalid severity {severity}")
        return cls(
            id=f"ISSUE-{uuid.uuid4().hex[:8]}",
            category=category,
            severity=severity,
            description=description,
            location=location or {},
            created_at=now_iso(),
            **extra,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _ensure_dir() -> None:
    ensure_layout()
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def save_issue(issue: Issue) -> Issue:
    _ensure_dir()
    with open(ISSUES_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(issue.to_dict(), ensure_ascii=False) + "\n")
    emit("ISSUE_SAVED", issue=issue.id, severity=issue.severity,
         category=issue.category)
    return issue


def save_all(issues: List[Issue]) -> List[Issue]:
    for i in issues:
        save_issue(i)
    return issues


def load_issues() -> List[Dict[str, Any]]:
    if not ISSUES_PATH.exists():
        return []
    out: List[Dict[str, Any]] = []
    for line in ISSUES_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def open_issues() -> List[Dict[str, Any]]:
    return [i for i in load_issues() if i.get("status") == "OPEN"]


def reset() -> None:
    if ISSUES_PATH.exists():
        ISSUES_PATH.unlink()
