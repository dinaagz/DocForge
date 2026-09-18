"""Controller — meta-supervisor of the system itself.

Detects: stagnation, oscillation, repeated errors, conflicts, no progress.
Can order the Planner to replan. Signals BLOCKED when nothing else helps.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List

from .events import emit
from .memory import record
from .planner import Planner
from .tasks import TaskQueue


class Controller:
    def __init__(self, queue: TaskQueue, planner: Planner,
                 config: Dict[str, Any]) -> None:
        self.queue = queue
        self.planner = planner
        self.max_global = config.get("processing", {}).get("max_global_iterations", 5)
        self.history: List[Dict[str, int]] = []

    def snapshot(self) -> Dict[str, int]:
        c = self.queue.counts()
        snap = {
            "COMPLETED": c.get("COMPLETED", 0),
            "FAILED": c.get("FAILED", 0),
            "PENDING_MANUAL": c.get("PENDING_MANUAL", 0),
            "PENDING": c.get("PENDING", 0),
            "RETRYING": c.get("RETRYING", 0),
        }
        self.history.append(snap)
        return snap

    def detect_stagnation(self) -> bool:
        if len(self.history) < 3:
            return False
        last = self.history[-3:]
        return all(s == last[0] for s in last)

    def detect_regression(self) -> bool:
        if len(self.history) < 2:
            return False
        prev, cur = self.history[-2], self.history[-1]
        return cur["COMPLETED"] < prev["COMPLETED"]

    def decide(self, iteration: int) -> str:
        """Return one of: CONTINUE, REPLAN, DONE, BLOCKED, DONE_WITH_REVIEW_ITEMS."""
        snap = self.snapshot()
        if self.queue.all_terminal():
            if snap["FAILED"] == 0 and snap["PENDING_MANUAL"] == 0:
                emit("CONTROLLER_DONE")
                return "DONE"
            if snap["PENDING_MANUAL"] > 0 or snap["FAILED"] < 3:
                emit("CONTROLLER_DONE_REVIEW", snap=snap)
                return "DONE_WITH_REVIEW_ITEMS"
            emit("CONTROLLER_BLOCKED", snap=snap)
            return "BLOCKED"

        if iteration >= self.max_global:
            emit("CONTROLLER_BUDGET_HIT", iteration=iteration)
            return "BLOCKED"

        if self.detect_stagnation():
            self.planner.replan("stagnation")
            record("controller", event="replan", reason="stagnation")
            return "REPLAN"

        if self.detect_regression():
            self.planner.replan("regression")
            record("controller", event="replan", reason="regression")
            return "REPLAN"

        return "CONTINUE"
