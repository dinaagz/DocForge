"""Planner — decomposes an objective into a task graph.

Produces tasks with dependencies. Does not execute anything.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .events import emit
from .memory import decision
from .tasks import Task, TaskQueue


class Planner:
    """Builds the initial task graph and re-plans on demand."""

    def __init__(self, queue: TaskQueue, config: Dict[str, Any]) -> None:
        self.queue = queue
        self.config = config

    def plan_initial(self) -> List[Task]:
        """Full-document plan: extraction → canonical model → parallel
        analysis branches → reconstruction → QA → export → report.
        """
        emit("PLAN_INITIAL_START")
        q = self.queue
        added: List[Task] = []

        # 1. Extraction
        t_ext = q.add("extract", agent="extractor",
                      priority=10, success_criteria=["work/inspection/paragraphs.json exists"])
        added.append(t_ext)

        # 2. Structure extraction (raw)
        t_struct_raw = q.add("structure_extract", agent="structure-architect",
                             priority=20, dependencies=[t_ext.id])
        added.append(t_struct_raw)

        # 3. Canonical model
        t_can = q.add("canonical_build", agent="canonical-builder",
                      priority=25, dependencies=[t_struct_raw.id])
        added.append(t_can)

        # 4. Parallel analysis branches (independent) — all depend on canonical
        parallel = [
            ("language_analyze", "language-editor", ["language"]),
            ("coherence_analyze", "coherence-agent", ["coherence"]),
            ("structure_verify", "structure-verifier", ["structure"]),
        ]
        pids = []
        for typ, ag, locks in parallel:
            t = q.add(typ, agent=ag, priority=40, dependencies=[t_can.id],
                     resource_locks=[f"branch:{locks[0]}"])
            pids.append(t.id)
            added.append(t)

        # 5. Reconstruction (apply structure, styles) — after analysis
        t_apply = q.add("structure_apply", agent="structure-applier",
                        priority=60, dependencies=pids)
        added.append(t_apply)
        t_manifest = q.add("manifest_build", agent="manifest-builder",
                           priority=61, dependencies=[t_apply.id])
        added.append(t_manifest)
        t_format = q.add("format_document", agent="formatting-agent",
                         priority=62, dependencies=[t_manifest.id])
        added.append(t_format)

        # 6. Assembly
        t_asm = q.add("assemble", agent="assembler", priority=70,
                      dependencies=[t_format.id])
        added.append(t_asm)

        # 7. Global verifiers (parallel)
        verifier_deps = [t_asm.id]
        vids = []
        for ag in ("integrity-verifier", "format-verifier",
                    "language-verifier", "structure-verifier"):
            t = q.add("verify", agent=ag, priority=80,
                     dependencies=verifier_deps)
            vids.append(t.id)
            added.append(t)

        # 8. Export
        t_exp = q.add("export", agent="exporter", priority=90,
                      dependencies=vids)
        added.append(t_exp)

        # 9. PDF verification
        t_pdf = q.add("pdf_verify", agent="pdf-verifier", priority=91,
                     dependencies=[t_exp.id])
        added.append(t_pdf)

        # 10. Final report
        t_rep = q.add("final_report", agent="report-agent", priority=100,
                     dependencies=[t_pdf.id])
        added.append(t_rep)

        decision("initial-plan", choice=f"{len(added)} tasks",
                 rationale="standard pipeline with parallel analysis+verification")
        emit("PLAN_INITIAL_DONE", tasks=len(added))
        return added

    def replan(self, reason: str) -> None:
        """Add remedial tasks based on failed verifiers."""
        emit("REPLAN", reason=reason)
        decision("replan", choice="add corrective tasks", rationale=reason)
        # Add corrective format/language passes if failed verifiers exist
        for t in self.queue.by_status("FAILED"):
            if t.agent == "format-verifier":
                self.queue.add("format_document", agent="formatting-agent",
                              priority=55, parent_task=t.id)
            elif t.agent == "language-verifier":
                self.queue.add("language_fix", agent="language-editor",
                              priority=55, parent_task=t.id)
