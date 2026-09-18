"""DocForge CLI — the unique user entry point.

Commands: init, run, status, workers, providers, audit, report,
resume, pause, stop, reset, doctor, install.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .capabilities import detect
from .config import load_config
from .events import emit
from .orchestrator import Orchestrator
from .paths import (DOCFORGE_DIR, LEGACY_STATE_DIR, OUTPUT_DIR, ROOT,
                    STATE_DIR, WORK_DIR, ensure_layout)
from .providers import available as providers_available
from .state import store
from .tasks import TaskQueue
from .workers import list_workers


# ── commands ────────────────────────────────────────────────

def cmd_init(_: argparse.Namespace) -> int:
    ensure_layout()
    _seed_default_configs()
    print(f"DocForge initialisé dans {DOCFORGE_DIR}")
    return 0


def _seed_default_configs() -> None:
    # Only create profiles that are missing — never overwrite user edits.
    seeds = {
        "academic.yaml": (
            "style:\n  language: fr\n  tone: professionnel\n  voice: académique\n"
            "  personality: neutre\n  formality: élevée\n  audience: universitaire\n"
            "  preserve_author_voice: true\nprocessing:\n  concurrency: 4\n"
        ),
        "corporate.yaml": (
            "style:\n  language: fr\n  tone: professionnel\n  voice: institutionnel\n"
            "  formality: élevée\n  audience: dirigeants\n"
        ),
        "minimal.yaml": (
            "style:\n  language: fr\n  tone: neutre\n  formality: moyenne\n"
        ),
    }
    prof_dir = DOCFORGE_DIR / "profiles"
    prof_dir.mkdir(parents=True, exist_ok=True)
    for name, body in seeds.items():
        p = prof_dir / name
        if not p.exists():
            p.write_text(body, encoding="utf-8")


def cmd_status(_: argparse.Namespace) -> int:
    sys_state = store.load("system", {"status": "INIT", "iteration": 0})
    q = TaskQueue()
    counts = q.counts()
    print(f"""
╔══════════════════════════════════════════════════╗
║               D O C F O R G E                    ║
╠══════════════════════════════════════════════════╣
║ Statut       : {sys_state.get('status', '—'):<32s} ║
║ Itération    : {str(sys_state.get('iteration', 0)):<32s} ║
║ Tâches       : {str(sum(counts.values())):<32s} ║
║ Complétées   : {str(counts.get('COMPLETED', 0)):<32s} ║
║ En cours     : {str(counts.get('RUNNING', 0)):<32s} ║
║ En attente   : {str(counts.get('PENDING', 0)):<32s} ║
║ Échouées     : {str(counts.get('FAILED', 0)):<32s} ║
║ Revue manuelle: {str(counts.get('PENDING_MANUAL', 0)):<31s} ║
╚══════════════════════════════════════════════════╝
""")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    ensure_layout()
    orch = Orchestrator()
    outcome = orch.run(budget_seconds=args.budget)
    print(f"Résultat : {outcome}")
    cmd_status(args)
    return 0 if outcome in ("DONE", "DONE_WITH_REVIEW_ITEMS") else 2


def cmd_workers(_: argparse.Namespace) -> int:
    print("Workers enregistrés :")
    for w in list_workers():
        print(f"  - {w}")
    return 0


def cmd_providers(_: argparse.Namespace) -> int:
    print("Providers disponibles :")
    for p in providers_available():
        print(f"  - {p}")
    return 0


def cmd_audit(_: argparse.Namespace) -> int:
    q = TaskQueue()
    for t in q.tasks.values():
        print(f"{t.id}  {t.status:<12s} {t.agent:<22s} {t.type}")
    return 0


def cmd_report(_: argparse.Namespace) -> int:
    from .report import build_report
    md, js = build_report()
    print(f"Rapport : {md}")
    print(f"JSON    : {js}")
    return 0


def cmd_reset(args: argparse.Namespace) -> int:
    if not args.force:
        print("Ajoutez --force pour confirmer la remise à zéro.")
        return 1
    for name in ("system", "tasks", "manual_review"):
        p = STATE_DIR / f"{name}.json"
        if p.exists():
            p.unlink()
    for name in ("loop_state", "chapter_status", "quality_log",
                  "structure_locked", "structure_proposal"):
        p = LEGACY_STATE_DIR / f"{name}.json"
        if p.exists():
            p.unlink()
    for d in (WORK_DIR / "inspection", WORK_DIR / "chapters",
              WORK_DIR / "qa", WORK_DIR / "assembled"):
        if d.exists():
            shutil.rmtree(d)
            d.mkdir(parents=True)
    for f in OUTPUT_DIR.glob("*"):
        if f.name != ".gitkeep":
            if f.is_dir():
                shutil.rmtree(f)
            else:
                f.unlink()
    emit("SYSTEM_RESET")
    print("État réinitialisé.")
    return 0


def cmd_doctor(_: argparse.Namespace) -> int:
    caps = detect()
    print("── DocForge Doctor ──")
    for k, v in caps.items():
        if k == "providers":
            print(f"  {k}:")
            for p, ok in v.items():
                print(f"    {p:<14s} {'AVAILABLE' if ok else 'NOT FOUND'}")
        else:
            print(f"  {k:<16s} {'OK' if v else 'MISSING'}")
    return 0


def cmd_install(_: argparse.Namespace) -> int:
    cmd_init(None)  # type: ignore[arg-type]
    print("Pour une installation complète : ./install.sh")
    return 0


def cmd_pause(_: argparse.Namespace) -> int:
    store.update("system", status="PAUSED")
    print("En pause. Utilisez `docforge run` pour reprendre.")
    return 0


def cmd_stop(_: argparse.Namespace) -> int:
    store.update("system", status="STOPPED")
    print("Arrêté.")
    return 0


# ── entry ───────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="docforge",
        description="DocForge — moteur autonome multi-agents de reconstruction, "
                    "correction, mise en forme et contrôle qualité documentaire.")
    p.add_argument("--version", action="version", version=f"DocForge {__version__}")
    sub = p.add_subparsers(dest="command", required=False)

    for name, fn in (("init", cmd_init), ("status", cmd_status),
                     ("workers", cmd_workers), ("providers", cmd_providers),
                     ("audit", cmd_audit), ("report", cmd_report),
                     ("doctor", cmd_doctor), ("install", cmd_install),
                     ("pause", cmd_pause), ("stop", cmd_stop)):
        s = sub.add_parser(name)
        s.set_defaults(func=fn)

    r = sub.add_parser("run")
    r.add_argument("--budget", type=int, default=None, help="Budget en secondes")
    r.set_defaults(func=cmd_run)

    res = sub.add_parser("resume")
    res.add_argument("--budget", type=int, default=None)
    res.set_defaults(func=cmd_run)

    rst = sub.add_parser("reset")
    rst.add_argument("--force", action="store_true")
    rst.set_defaults(func=cmd_reset)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
