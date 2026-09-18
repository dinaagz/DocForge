"""Concurrent task scheduler — real parallel execution when supported.

Uses a thread pool by default. Resource-lock aware: two tasks that
claim the same lock cannot run at the same time.
"""
from __future__ import annotations

import time
import traceback
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Lock
from typing import Any, Callable, Dict, Optional, Set

from .events import emit
from .memory import record
from .tasks import Task, TaskQueue


class ResourceLocks:
    def __init__(self) -> None:
        self._held: Set[str] = set()
        self._m = Lock()

    def try_acquire(self, keys):
        with self._m:
            keys = list(keys)
            if any(k in self._held for k in keys):
                return False
            self._held.update(keys)
            return True

    def release(self, keys) -> None:
        with self._m:
            for k in keys:
                self._held.discard(k)


Runner = Callable[[Task], Dict[str, Any]]


class Scheduler:
    """Drives a TaskQueue with a bounded pool of workers."""

    def __init__(self, queue: TaskQueue, runner: Runner,
                 max_workers: int = 4, poll_interval: float = 0.05) -> None:
        self.queue = queue
        self.runner = runner
        self.max_workers = max_workers
        self.poll_interval = poll_interval
        self.locks = ResourceLocks()

    def _wrap(self, task: Task) -> Callable[[], Any]:
        def _call():
            try:
                out = self.runner(task) or {}
                self.locks.release(task.resource_locks)
                self.queue.mark(task.id, "COMPLETED", output=out)
                record("task_completed", task=task.id, agent=task.agent, output=out)
            except Exception as e:  # noqa: BLE001
                self.locks.release(task.resource_locks)
                tb = traceback.format_exc(limit=3)
                emit("TASK_EXCEPTION", task=task.id, err=str(e), tb=tb)
                self.queue.retry(task.id, error=str(e))
        return _call

    def run_until_done(self, budget_seconds: Optional[int] = None) -> Dict[str, int]:
        """Run tasks until the queue reaches a terminal collective state."""
        started = time.time()
        futures: Dict[str, Future] = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            while True:
                # Reap
                done_ids = [tid for tid, f in futures.items() if f.done()]
                for tid in done_ids:
                    futures.pop(tid, None)

                # Fill
                for task in self.queue.ready():
                    if len(futures) >= self.max_workers:
                        break
                    if task.id in futures:
                        continue
                    if task.resource_locks and not self.locks.try_acquire(task.resource_locks):
                        continue
                    self.queue.mark(task.id, "RUNNING")
                    futures[task.id] = ex.submit(self._wrap(task))

                if not futures and self.queue.all_terminal():
                    break
                if budget_seconds and (time.time() - started) > budget_seconds:
                    emit("SCHEDULER_BUDGET_EXHAUSTED", budget=budget_seconds)
                    break
                time.sleep(self.poll_interval)

        counts = self.queue.counts()
        emit("SCHEDULER_DONE", counts=counts)
        return counts
