"""Manager — dispatches tasks to providers/workers via the scheduler.

Owns the runner function the scheduler consumes. Also owns the canonical
model build (special task type) and the manual review queue.
"""
from __future__ import annotations

from typing import Any, Dict

from .canonical import build_from_inspection
from .events import emit
from .memory import record
from .paths import MANUAL_REVIEW_PATH
from .providers import select as select_provider
from .providers.base import ProviderResult
from .state import store
from .tasks import Task, TaskQueue


class Manager:
    """Distributes tasks to the right provider/worker."""

    def __init__(self, queue: TaskQueue, config: Dict[str, Any]) -> None:
        self.queue = queue
        self.config = config
        self.provider = select_provider(config.get("providers", {}).get("preferred", ["generic"]))
        emit("PROVIDER_SELECTED", name=self.provider.name)

    def run(self, task: Task) -> Dict[str, Any]:
        # Special task types handled inline
        if task.type == "canonical_build":
            model = build_from_inspection()
            return {"chapters": len(model.get("chapters", [])),
                    "paragraphs": len(model.get("paragraphs", []))}

        result: ProviderResult = self.provider.run_agent(task.agent, task.type, context={
            **task.input, "task_id": task.id, "task_type": task.type,
        })
        if not result.ok:
            raise RuntimeError(result.error or "provider failed")

        # If a verifier returned FAIL, log it but don't raise — the
        # Controller can decide to replan.
        out = dict(result.output)
        if out.get("verdict") == "FAIL":
            record("verify_fail", task=task.id, agent=task.agent, output=out)
        return out

    def flag_manual(self, task: Task, reason: str) -> None:
        current = store.load("manual_review", {"items": []})
        current.setdefault("items", []).append({
            "id": f"ISSUE-{task.id}",
            "task": task.id, "agent": task.agent,
            "reason": reason, "confidence": "LOW",
            "action": "NO_AUTO_CHANGE", "workflow": "CONTINUE",
        })
        store.save("manual_review", current)
        self.queue.mark(task.id, "PENDING_MANUAL", error=reason)
        emit("MANUAL_REVIEW", task=task.id, reason=reason)
