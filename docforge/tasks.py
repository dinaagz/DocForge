"""Task model and TaskQueue with dependencies, priorities, retries.

The queue is persistent (state/tasks.json). Any worker can be resumed.
"""
from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from .events import emit, now_iso
from .state import store

TASK_STATES = (
    "PENDING", "READY", "RUNNING", "WAITING", "COMPLETED",
    "FAILED", "RETRYING", "BLOCKED", "PENDING_MANUAL",
)


@dataclass
class Task:
    id: str
    type: str
    agent: str = ""
    provider: str = "generic"
    status: str = "PENDING"
    priority: int = 100
    dependencies: List[str] = field(default_factory=list)
    parent_task: Optional[str] = None
    input: Dict[str, Any] = field(default_factory=dict)
    output: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    resource_locks: List[str] = field(default_factory=list)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    branch: Optional[str] = None
    success_criteria: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TaskQueue:
    """Persistent, dependency-aware task queue."""

    STATE_KEY = "tasks"

    def __init__(self) -> None:
        self._load()

    # ── persistence ────────────────────────────────────────────

    def _load(self) -> None:
        raw = store.load(self.STATE_KEY, {"tasks": []})
        self.tasks: Dict[str, Task] = {}
        for t in raw.get("tasks", []):
            self.tasks[t["id"]] = Task(**t)

    def _save(self) -> None:
        store.save(self.STATE_KEY, {"tasks": [t.to_dict() for t in self.tasks.values()]})

    # ── mutation ───────────────────────────────────────────────

    def add(self, type: str, **kwargs: Any) -> Task:
        tid = kwargs.pop("id", None) or f"T-{uuid.uuid4().hex[:8]}"
        task = Task(id=tid, type=type, **kwargs)
        self.tasks[tid] = task
        self._save()
        emit("TASK_ADDED", task=tid, type=type, agent=task.agent, deps=task.dependencies)
        return task

    def mark(self, tid: str, status: str, **fields: Any) -> Task:
        if tid not in self.tasks:
            raise KeyError(tid)
        t = self.tasks[tid]
        if status not in TASK_STATES:
            raise ValueError(f"invalid status {status}")
        t.status = status
        if status == "RUNNING" and not t.started_at:
            t.started_at = now_iso()
        if status in ("COMPLETED", "FAILED"):
            t.completed_at = now_iso()
        for k, v in fields.items():
            setattr(t, k, v)
        self._save()
        emit("TASK_STATUS", task=tid, status=status)
        return t

    def retry(self, tid: str, error: str = "") -> Optional[Task]:
        t = self.tasks[tid]
        t.retry_count += 1
        t.error = error
        if t.retry_count > t.max_retries:
            return self.mark(tid, "FAILED", error=f"max retries: {error}")
        return self.mark(tid, "RETRYING")

    # ── queries ────────────────────────────────────────────────

    def by_status(self, *statuses: str) -> List[Task]:
        return [t for t in self.tasks.values() if t.status in statuses]

    def ready(self) -> List[Task]:
        """Tasks whose deps are COMPLETED and status is PENDING or RETRYING."""
        done = {t.id for t in self.tasks.values() if t.status == "COMPLETED"}
        out: List[Task] = []
        for t in self.tasks.values():
            if t.status not in ("PENDING", "RETRYING"):
                continue
            if all(d in done for d in t.dependencies):
                out.append(t)
        out.sort(key=lambda x: (x.priority, x.id))
        return out

    def all_terminal(self) -> bool:
        return all(t.status in ("COMPLETED", "FAILED", "PENDING_MANUAL", "BLOCKED")
                   for t in self.tasks.values())

    def counts(self) -> Dict[str, int]:
        c: Dict[str, int] = {}
        for t in self.tasks.values():
            c[t.status] = c.get(t.status, 0) + 1
        return c
