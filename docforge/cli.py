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
    (DOCFORGE_DIR / "profiles" / "academic.yaml").write_text(
        "style:\n  language: fr\n  tone: professionnel\n  voice: académique\n"
        "  personality: neutre\n  formality: élevée\n  audience: universitaire\n"
        "  preserve_author_voice: true\nprocessing:\n  concurrency: 4\n",
        encoding="utf-8")
    (DOCFORGE_DIR / "profiles" / "corporate.yaml").write_text(
        "style:\n  language: fr\n  tone: professionnel\n  voice: institutionnel\n"
        "  formality: élevée\n  audience: dirigeants\n",
        encoding="utf-8")
    (DOCFORGE_DIR / "profiles" / "minimal.yaml").write_text(
        "style:\n  language: fr\n  tone: neutre\n  formality: moyenne\n",
        encoding="utf-8")


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


# ── Universal DocForge commands ──────────────────────────────

def cmd_interview(_: argparse.Namespace) -> int:
    from .contract.interviewer import questions
    for q in questions():
        print(f"[{q['key']}] {q['prompt']}")
    print("\nCollectez les réponses puis appelez :")
    print("  from docforge.contract.interviewer import write_contract")
    print("  write_contract(<answers>)")
    return 0


def cmd_audit_engine(_: argparse.Namespace) -> int:
    from .audit.engine import run_audit
    from .audit.issues import save_all, load_issues
    from .canonical import load_canonical, new_model
    issues = run_audit(load_canonical() or new_model(), persist=True)
    print(f"{len(issues)} anomalie(s) détectée(s), total historique : "
          f"{len(load_issues())}")
    return 0


def cmd_plan(_: argparse.Namespace) -> int:
    from .audit.checklist import build_from_registry
    p = build_from_registry()
    print(f"Checklist écrite : {p}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    from .completion.gates import evaluate, evaluate_all, load_gates
    if args.gate:
        r = evaluate(args.gate)
        print(f"{args.gate}: {r['verdict']} — {r.get('reason', '')}")
        return 0 if r["verdict"] == "PASS" else 2
    results = evaluate_all()
    failed = [gid for gid, r in results.items() if r["verdict"] != "PASS"]
    for gid, r in results.items():
        print(f"  {gid:<16s} {r['verdict']}")
    print(f"{len(results) - len(failed)}/{len(results)} gates PASS")
    return 0 if not failed else 2


def cmd_score(_: argparse.Namespace) -> int:
    from .completion.gates import evaluate_all
    from .completion.score import compute
    results = evaluate_all(record_evidence=False)
    passed = sum(1 for r in results.values() if r["verdict"] == "PASS")
    ratio = 100.0 * passed / max(1, len(results))
    s = compute({"completeness": ratio, "requirement_coverage": ratio,
                 "verification_quality": ratio, "correctness": ratio,
                 "consistency": ratio})
    print(f"Score total : {s['total']}/100 sur {s['n_dimensions']} dimensions")
    for k, v in s["dimensions"].items():
        print(f"  {k:<24s} {v:.1f}")
    return 0


def cmd_improve(args: argparse.Namespace) -> int:
    from .improvement.loop import run_bounded
    r = run_bounded(max_iterations=args.max_iters)
    print(f"Boucle terminée ({r['reason']}), {r['iterations']} itération(s)")
    if r.get("best"):
        print(f"Meilleur score : {r['best'].get('total')}")
    return 0


def cmd_final_audit(_: argparse.Namespace) -> int:
    from .completion.completion_guard import evaluate
    r = evaluate()
    print(f"Verdict : {r['verdict']}")
    print(f"Gates requises : {r['required_total']}, passées : {len(r['passed'])}")
    if r["unmet"]:
        print("Gates non satisfaites :")
        for u in r["unmet"]:
            print(f"  - {u['gate']}: {u['reason']}")
    if r["contract_coverage"]["missing"]:
        print("Exigences non couvertes :")
        for m in r["contract_coverage"]["missing"]:
            print(f"  - {m}")
    return 0 if r["verdict"] == "DONE" else 2


def _format_dispatch(op: str, path: str) -> int:
    from .formats import get, NotAvailable
    p = Path(path)
    if not p.exists():
        print(f"Fichier introuvable : {path}")
        return 2
    ext = p.suffix.lower().lstrip(".")
    mapping = {"md": "markdown", "markdown": "markdown", "docx": "docx",
               "txt": "txt"}
    fmt = mapping.get(ext, ext)
    try:
        adapter = get(fmt)
    except NotAvailable as e:
        print(str(e))
        return 2
    if not adapter.implemented:
        print(f"Format {fmt} déclaré mais non implémenté (stub).")
        return 2
    try:
        result = getattr(adapter, op)(p)
    except NotAvailable as e:
        print(str(e))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    return _format_dispatch("inspect", args.path)


def cmd_structure(args: argparse.Namespace) -> int:
    return _format_dispatch("extract", args.path)


def cmd_language(_: argparse.Namespace) -> int:
    from .completion.gates import evaluate
    r = evaluate("G-NOREG")
    print(f"Langue et tests : {r['verdict']}")
    return 0 if r["verdict"] == "PASS" else 2


def cmd_format_cmd(args: argparse.Namespace) -> int:
    return _format_dispatch("validate", args.path)


def cmd_layout(args: argparse.Namespace) -> int:
    return _format_dispatch("validate", args.path)


def cmd_visual(_: argparse.Namespace) -> int:
    from .completion.completion_guard import evaluate
    r = evaluate()
    print(f"Audit visuel (guard-based) : {r['verdict']}")
    return 0


def cmd_tables(args: argparse.Namespace) -> int:
    return _format_dispatch("extract", args.path)


def cmd_figures(args: argparse.Namespace) -> int:
    return _format_dispatch("extract", args.path)


def cmd_formulas(args: argparse.Namespace) -> int:
    return _format_dispatch("extract", args.path)


def cmd_references(args: argparse.Namespace) -> int:
    return _format_dispatch("extract", args.path)


# ── entry ───────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="docforge",
        description="DocForge — moteur autonome multi-agents de reconstruction, "
                    "correction, mise en forme et contrôle qualité documentaire.")
    p.add_argument("--version", action="version", version=f"DocForge {__version__}")
    sub = p.add_subparsers(dest="command", required=False)

    # NOTE: `audit` is bound to the audit engine (issue registry); the
    # previous task-listing behavior moves to `audit-tasks`.
    for name, fn in (("init", cmd_init), ("status", cmd_status),
                     ("workers", cmd_workers), ("providers", cmd_providers),
                     ("audit-tasks", cmd_audit),
                     ("audit", cmd_audit_engine),
                     ("report", cmd_report),
                     ("doctor", cmd_doctor), ("install", cmd_install),
                     ("pause", cmd_pause), ("stop", cmd_stop),
                     ("interview", cmd_interview),
                     ("plan", cmd_plan),
                     ("score", cmd_score),
                     ("visual", cmd_visual),
                     ("final-audit", cmd_final_audit),
                     ("language", cmd_language)):
        s = sub.add_parser(name)
        s.set_defaults(func=fn)

    v = sub.add_parser("verify")
    v.add_argument("--gate", default=None,
                   help="ID de la gate; vide = toutes")
    v.set_defaults(func=cmd_verify)

    imp = sub.add_parser("improve")
    imp.add_argument("--max-iters", type=int, default=3,
                     dest="max_iters")
    imp.set_defaults(func=cmd_improve)

    for name, fn in (("inspect", cmd_inspect), ("structure", cmd_structure),
                     ("format", cmd_format_cmd), ("layout", cmd_layout),
                     ("tables", cmd_tables), ("figures", cmd_figures),
                     ("formulas", cmd_formulas),
                     ("references", cmd_references)):
        p2 = sub.add_parser(name)
        p2.add_argument("path")
        p2.set_defaults(func=fn)

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
