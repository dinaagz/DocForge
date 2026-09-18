"""Tests du cœur DocForge : state, tasks, scheduler, planner, controller,
capacités, providers, canonical, workers, orchestrateur, rapport.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import pytest


@pytest.fixture()
def tmp_root(tmp_path, monkeypatch):
    """Isole DocForge dans un dossier temporaire."""
    (tmp_path / "input").mkdir()
    (tmp_path / "work").mkdir()
    (tmp_path / "output").mkdir()
    (tmp_path / "logs").mkdir()
    (tmp_path / "scripts").mkdir()
    monkeypatch.setenv("DOCFORGE_ROOT", str(tmp_path))
    # Purge cached modules referring to old paths
    import importlib, sys
    for mod in list(sys.modules):
        if mod.startswith("docforge"):
            del sys.modules[mod]
    return tmp_path


def test_state_atomic(tmp_root):
    from docforge.state import Store
    st = Store()
    st.save("demo", {"a": 1})
    assert st.load("demo") == {"a": 1}
    st.update("demo", b=2)
    assert st.load("demo") == {"a": 1, "b": 2}


def test_task_queue_deps(tmp_root):
    from docforge.tasks import TaskQueue
    q = TaskQueue()
    a = q.add("first", agent="ext", priority=1)
    b = q.add("second", agent="fmt", dependencies=[a.id])
    ready_ids = [t.id for t in q.ready()]
    assert a.id in ready_ids
    assert b.id not in ready_ids
    q.mark(a.id, "COMPLETED")
    ready_ids = [t.id for t in q.ready()]
    assert b.id in ready_ids


def test_scheduler_parallel(tmp_root):
    """TEST A : deux agents indépendants tournent simultanément."""
    from docforge.scheduler import Scheduler
    from docforge.tasks import TaskQueue

    q = TaskQueue()
    q.add("a", agent="w1")
    q.add("b", agent="w2")

    started_at = {}
    def runner(task):
        started_at[task.id] = time.time()
        time.sleep(0.2)
        return {"ok": True}
    Scheduler(q, runner, max_workers=2).run_until_done()
    # If truly parallel, the two started within a small window
    times = sorted(started_at.values())
    assert times[1] - times[0] < 0.15


def test_scheduler_isolates_failure(tmp_root):
    """TEST B : un agent échoue, les autres continuent."""
    from docforge.scheduler import Scheduler
    from docforge.tasks import TaskQueue
    q = TaskQueue()
    q.add("ok", agent="a", max_retries=0)
    q.add("bad", agent="b", max_retries=0)
    def runner(task):
        if task.agent == "b":
            raise RuntimeError("boom")
        return {"ok": True}
    Scheduler(q, runner, max_workers=2).run_until_done()
    counts = q.counts()
    assert counts.get("COMPLETED", 0) == 1
    assert counts.get("FAILED", 0) == 1


def test_scheduler_resource_lock(tmp_root):
    """TEST E : deux tâches sur la même ressource se sérialisent."""
    from docforge.scheduler import Scheduler
    from docforge.tasks import TaskQueue
    q = TaskQueue()
    q.add("x", agent="a", resource_locks=["shared"])
    q.add("y", agent="b", resource_locks=["shared"])
    overlap = []
    running = []
    def runner(task):
        running.append(task.id)
        overlap.append(len(running))
        time.sleep(0.1)
        running.remove(task.id)
        return {}
    Scheduler(q, runner, max_workers=4).run_until_done()
    assert max(overlap) == 1


def test_capabilities_detect(tmp_root):
    from docforge.capabilities import detect
    caps = detect()
    assert caps["filesystem"]
    assert isinstance(caps["providers"], dict)
    assert "generic" in caps["providers"]


def test_providers_registry(tmp_root):
    from docforge.providers import available, select
    avail = available()
    assert "generic" in avail
    p = select(["nonexistent-x", "generic"])
    assert p.name == "generic"


def test_memory_traceability(tmp_root):
    from docforge.memory import decision, correction, why
    decision(topic="test", choice="A", rationale="parce que")
    correction(target="P000001", before="foo", after="bar", agent="fmt", rationale="typographie")
    hits = why("P000001")
    assert hits and hits[0]["target"] == "P000001"


def test_controller_stagnation(tmp_root):
    from docforge.controller import Controller
    from docforge.planner import Planner
    from docforge.tasks import TaskQueue
    q = TaskQueue()
    q.add("a", agent="x")
    planner = Planner(q, {"processing": {"max_global_iterations": 5}})
    ctrl = Controller(q, planner, {"processing": {"max_global_iterations": 5}})
    for _ in range(3):
        _ = ctrl.snapshot()
    assert ctrl.detect_stagnation()


def test_planner_builds_graph(tmp_root):
    from docforge.planner import Planner
    from docforge.tasks import TaskQueue
    q = TaskQueue()
    Planner(q, {}).plan_initial()
    assert len(q.tasks) >= 10
    # Report is last, depends on export
    types = {t.type for t in q.tasks.values()}
    for expected in ("extract", "canonical_build", "assemble",
                     "export", "final_report", "pdf_verify"):
        assert expected in types


def test_orchestrator_finishes_without_input(tmp_root):
    """TEST H : aucun document source → le système ne crashe pas,
    conclut proprement (DONE_WITH_REVIEW_ITEMS ou BLOCKED)."""
    from docforge.orchestrator import Orchestrator
    outcome = Orchestrator().run(budget_seconds=30)
    assert outcome in ("DONE", "DONE_WITH_REVIEW_ITEMS", "BLOCKED")


def test_report_in_french(tmp_root):
    """TEST J : rapport final produit en français."""
    from docforge.report import build_report
    md_path, _ = build_report()
    text = Path(md_path).read_text(encoding="utf-8")
    assert "Rapport DocForge" in text
    assert "Statut final" in text


def test_resume_persistence(tmp_root):
    """TEST D : l'état est persistant, la reprise fonctionne."""
    from docforge.tasks import TaskQueue
    q1 = TaskQueue()
    t = q1.add("x", agent="a")
    q1.mark(t.id, "RUNNING")
    q2 = TaskQueue()  # simulate restart
    assert t.id in q2.tasks
    assert q2.tasks[t.id].status == "RUNNING"
