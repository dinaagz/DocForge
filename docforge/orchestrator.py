"""Top-level orchestrator: PLAN → BUILD → VERIFY → MEMORY → CONTROL → REPLAN.

Fully autonomous. The only human intervention point is a manual review
queue that is consulted post-run — the workflow itself never stops for
approval (rule §15).
"""
from __future__ import annotations

from typing import Any, Dict

from .config import load_config
from .controller import Controller
from .events import emit
from .manager import Manager
from .paths import ensure_layout
from .planner import Planner
from .scheduler import Scheduler
from .state import store
from .tasks import TaskQueue


class Orchestrator:
    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        ensure_layout()
        self.config = config or load_config()
        self.queue = TaskQueue()
        self.planner = Planner(self.queue, self.config)
        self.manager = Manager(self.queue, self.config)
        self.controller = Controller(self.queue, self.planner, self.config)
        self.scheduler = Scheduler(
            self.queue, self.manager.run,
            max_workers=self.config.get("processing", {}).get("concurrency", 4),
        )

    def run(self, budget_seconds: int | None = None) -> str:
        """Runs to a terminal outcome. Returns the final status."""
        state = store.load("system", {"status": "INIT", "iteration": 0})
        state["status"] = "RUNNING"
        state["iteration"] = state.get("iteration", 0)
        store.save("system", state)
        emit("ORCH_START", concurrency=self.scheduler.max_workers,
             provider=self.manager.provider.name)

        # Plan if empty
        if not self.queue.tasks:
            self.planner.plan_initial()

        # Cycle: run → controller decides
        while True:
            self.scheduler.run_until_done(budget_seconds=budget_seconds)
            state["iteration"] = state.get("iteration", 0) + 1
            store.save("system", state)
            decision = self.controller.decide(state["iteration"])
            emit("ORCH_CYCLE", iteration=state["iteration"], decision=decision)
            if decision in ("DONE", "BLOCKED", "DONE_WITH_REVIEW_ITEMS"):
                state["status"] = decision
                store.save("system", state)
                return decision
            if decision == "REPLAN":
                continue
            if decision == "CONTINUE":
                continue
