#!/usr/bin/env python3
"""
loop.py — The agentic document-processing state machine.

This is the decision engine of the heartbeat loop.  It:
  1. Loads current state
  2. Decides the next action
  3. Executes the deterministic part (Python scripts)
  4. Persists state and logs
  5. Reports what Claude agents should do next

STATES:
  INIT -> INSPECTION -> STRUCTURE_ANALYSIS -> WAITING_FOR_HUMAN_VALIDATION
  -> STRUCTURE_LOCKED -> CHAPTER_PROCESSING -> CHAPTER_QA -> CHAPTER_VALIDATED
  -> NEXT_CHAPTER -> ASSEMBLY -> GLOBAL_QA -> EXPORT -> FINAL_REPORT -> DONE

BRANCHES:
  CHAPTER_QA -> FAIL -> TARGETED_CORRECTION -> CHAPTER_QA  (max 5)
  CHAPTER_QA -> 5 fails -> PENDING_MANUAL -> NEXT_CHAPTER
  GLOBAL_QA  -> FAIL -> TARGETED_GLOBAL_CORRECTION -> GLOBAL_QA  (max 5)
  GLOBAL_QA  -> 5 fails -> BLOCKED
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure scripts/ is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (
    INPUT_DIR, LOGS_DIR, OUTPUT_DIR, PROJECT_ROOT, STATE_DIR, WORK_DIR,
    get_logger, load_config, load_state, log_event, now_iso, save_state,
)

logger = get_logger("loop")

# ── All valid states ────────────────────────────────────────────
STATES = [
    "INIT",
    "INSPECTION",
    "STRUCTURE_ANALYSIS",
    "WAITING_FOR_HUMAN_VALIDATION",
    "STRUCTURE_LOCKED",
    "CHAPTER_PROCESSING",
    "CHAPTER_QA",
    "TARGETED_CORRECTION",
    "CHAPTER_VALIDATED",
    "NEXT_CHAPTER",
    "ASSEMBLY",
    "GLOBAL_QA",
    "TARGETED_GLOBAL_CORRECTION",
    "EXPORT",
    "FINAL_REPORT",
    "DONE",
    "BLOCKED",
    "FAILED",
    "PENDING_MANUAL",
]

# ── Lock management ────────────────────────────────────────────

LOCK_PATH = STATE_DIR / ".loop.lock"


def acquire_lock() -> bool:
    if LOCK_PATH.exists():
        # Check if stale (older than 30 minutes)
        age = time.time() - LOCK_PATH.stat().st_mtime
        if age < 1800:
            logger.error("Loop already running (lock age: %.0fs)", age)
            return False
        logger.warning("Stale lock detected (%.0fs old), removing", age)
        LOCK_PATH.unlink()

    LOCK_PATH.write_text(json.dumps({
        "pid": os.getpid(),
        "started_at": now_iso(),
    }))
    return True


def release_lock() -> None:
    if LOCK_PATH.exists():
        LOCK_PATH.unlink()


# ── State management ───────────────────────────────────────────

def get_loop_state() -> Dict[str, Any]:
    state = load_state("loop_state")
    if not state:
        state = {
            "workflow": "academic-document-processing",
            "status": "INIT",
            "current_phase": "INIT",
            "current_chapter": None,
            "last_successful_step": None,
            "last_error": None,
            "iteration": 0,
            "global_iteration": 0,
            "updated_at": now_iso(),
            "resume_required": False,
        }
        save_state("loop_state", state)
    return state


def set_phase(state: Dict[str, Any], phase: str, **extras: Any) -> Dict[str, Any]:
    state["current_phase"] = phase
    state["status"] = "PROCESSING" if phase not in ("DONE", "BLOCKED", "FAILED") else phase
    state["updated_at"] = now_iso()
    state.update(extras)
    save_state("loop_state", state)
    log_event("PHASE_CHANGE", phase=phase, **extras)
    logger.info("Phase -> %s %s", phase, extras if extras else "")
    return state


def set_error(state: Dict[str, Any], error: str) -> Dict[str, Any]:
    state["last_error"] = error
    state["updated_at"] = now_iso()
    save_state("loop_state", state)
    log_event("ERROR", error=error)
    logger.error("Error: %s", error)
    return state


# ── Script runners ─────────────────────────────────────────────

def run_script(name: str, *args: str, timeout: int = 600) -> Tuple[int, str, str]:
    """Run a script from scripts/ and return (exit_code, stdout, stderr)."""
    script = PROJECT_ROOT / "scripts" / name
    cmd = [sys.executable, str(script)] + list(args)
    logger.info("Running: %s", " ".join(cmd))
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=str(PROJECT_ROOT / "scripts"),
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Timeout after {timeout}s"
    except Exception as e:
        return -1, "", str(e)


# ── Current chapter helpers ────────────────────────────────────

def get_current_chapter(state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    ch_status = load_state("chapter_status")
    if not ch_status or not ch_status.get("chapters"):
        return None

    cid = state.get("current_chapter")
    if cid:
        for ch in ch_status["chapters"]:
            if ch["id"] == cid:
                return ch
    return None


def find_next_chapter() -> Optional[Dict[str, Any]]:
    ch_status = load_state("chapter_status")
    if not ch_status:
        return None
    for ch in ch_status.get("chapters", []):
        if ch["status"] == "NOT_PROCESSED":
            return ch
    return None


def update_chapter(chapter_id: str, **updates: Any) -> None:
    ch_status = load_state("chapter_status")
    for ch in ch_status.get("chapters", []):
        if ch["id"] == chapter_id:
            ch.update(updates)
            break
    ch_status["last_updated"] = now_iso()
    save_state("chapter_status", ch_status)


def all_chapters_done() -> bool:
    ch_status = load_state("chapter_status")
    if not ch_status:
        return False
    for ch in ch_status.get("chapters", []):
        if ch["status"] not in ("VALIDATED", "PENDING_MANUAL"):
            return False
    return True


# ── State machine steps ───────────────────────────────────────

def step_init(state: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize the workflow — check prerequisites."""
    cfg = load_config()
    docx_path = INPUT_DIR / cfg["document"]["name"]

    if not docx_path.exists():
        return set_error(state, f"Input file not found: {docx_path}")

    # Clean working directories
    for d in [WORK_DIR / "inspection", WORK_DIR / "chapters",
              WORK_DIR / "qa", WORK_DIR / "assembled"]:
        d.mkdir(parents=True, exist_ok=True)

    return set_phase(state, "INSPECTION")


def step_inspection(state: Dict[str, Any]) -> Dict[str, Any]:
    """Run inspect_docx.py."""
    rc, out, err = run_script("inspect_docx.py")
    if rc != 0:
        return set_error(state, f"Inspection failed: {err}")

    state["last_successful_step"] = "INSPECTION"
    return set_phase(state, "STRUCTURE_ANALYSIS")


def step_structure_analysis(state: Dict[str, Any]) -> Dict[str, Any]:
    """Run extract_structure.py, then delegate to structure-analyst agent."""
    rc, out, err = run_script("extract_structure.py")
    if rc != 0:
        return set_error(state, f"Structure extraction failed: {err}")

    state["last_successful_step"] = "STRUCTURE_ANALYSIS"
    return set_phase(state, "WAITING_FOR_HUMAN_VALIDATION",
                     agent_action="STRUCTURE_ANALYST_REVIEW_NEEDED")


def step_waiting_for_validation(state: Dict[str, Any]) -> Dict[str, Any]:
    """Check if structure_locked.json exists."""
    locked = load_state("structure_locked")
    if locked and locked.get("validated", False):
        state["last_successful_step"] = "STRUCTURE_VALIDATED"
        return set_phase(state, "STRUCTURE_LOCKED")
    # Stay in waiting state
    logger.info("Still waiting for human validation of structure proposal")
    return state


def step_structure_locked(state: Dict[str, Any]) -> Dict[str, Any]:
    """Apply locked structure and create chapter manifest."""
    rc, out, err = run_script("apply_structure.py")
    if rc != 0:
        return set_error(state, f"Structure application failed: {err}")

    rc, out, err = run_script("create_manifest.py")
    if rc != 0:
        return set_error(state, f"Manifest creation failed: {err}")

    state["last_successful_step"] = "STRUCTURE_LOCKED"
    return set_phase(state, "CHAPTER_PROCESSING")


def step_chapter_processing(state: Dict[str, Any]) -> Dict[str, Any]:
    """Find next chapter to process and set it as current."""
    next_ch = find_next_chapter()
    if not next_ch:
        if all_chapters_done():
            return set_phase(state, "ASSEMBLY")
        return set_error(state, "No processable chapters found but not all done")

    cid = next_ch["id"]
    update_chapter(cid, status="PROCESSING", iterations=0)
    state["current_chapter"] = cid
    state["iteration"] = 0

    return set_phase(state, "CHAPTER_QA",
                     current_chapter=cid,
                     agent_action="PROCESS_CHAPTER")


def step_chapter_qa(state: Dict[str, Any]) -> Dict[str, Any]:
    """Run QA checks on current chapter. Delegates to quality-controller agent."""
    cfg = load_config()
    max_iter = cfg.get("processing", {}).get("max_quality_iterations", 5)
    cid = state.get("current_chapter")

    if not cid:
        return set_error(state, "No current chapter for QA")

    ch = get_current_chapter(state)
    if not ch:
        return set_error(state, f"Chapter {cid} not found in status")

    iteration = ch.get("iterations", 0) + 1
    update_chapter(cid, iterations=iteration, status="QA")
    state["iteration"] = iteration

    if iteration > max_iter:
        logger.warning("Chapter %s exceeded max iterations (%d)", cid, max_iter)
        update_chapter(cid, status="PENDING_MANUAL",
                       issues=ch.get("issues", []) + [f"Exceeded {max_iter} QA iterations"])
        log_event("CHAPTER_PENDING_MANUAL", chapter=cid, iterations=iteration)
        return set_phase(state, "NEXT_CHAPTER", current_chapter=cid)

    # The actual QA is done by agents — this signals what's needed
    return set_phase(state, "CHAPTER_QA",
                     iteration=iteration,
                     agent_action="RUN_QA_CHECKS")


def step_targeted_correction(state: Dict[str, Any]) -> Dict[str, Any]:
    """Signal that a targeted correction is needed on current chapter."""
    cid = state.get("current_chapter")
    return set_phase(state, "CHAPTER_QA",
                     agent_action="APPLY_TARGETED_CORRECTION",
                     current_chapter=cid)


def step_chapter_validated(state: Dict[str, Any]) -> Dict[str, Any]:
    """Mark current chapter as validated and move to next."""
    cid = state.get("current_chapter")
    if cid:
        update_chapter(cid, status="VALIDATED")
        log_event("CHAPTER_VALIDATED", chapter=cid)
    return set_phase(state, "NEXT_CHAPTER")


def step_next_chapter(state: Dict[str, Any]) -> Dict[str, Any]:
    """Advance to the next unprocessed chapter or to ASSEMBLY."""
    if all_chapters_done():
        return set_phase(state, "ASSEMBLY")
    return step_chapter_processing(state)


def step_assembly(state: Dict[str, Any]) -> Dict[str, Any]:
    """Run merge and formatting on assembled document."""
    rc, out, err = run_script("merge_docx.py")
    if rc != 0:
        return set_error(state, f"Merge failed: {err}")

    assembled = WORK_DIR / "assembled" / "merged.docx"
    if assembled.exists():
        # Apply styles
        rc2, out2, err2 = run_script("apply_styles.py", str(assembled))
        if rc2 != 0:
            logger.warning("Style application failed: %s", err2)

        # Update fields / TOC
        rc3, out3, err3 = run_script("update_fields.py", str(assembled))
        if rc3 != 0:
            logger.warning("Field update failed: %s", err3)

    state["last_successful_step"] = "ASSEMBLY"
    state["global_iteration"] = 0
    return set_phase(state, "GLOBAL_QA")


def step_global_qa(state: Dict[str, Any]) -> Dict[str, Any]:
    """Run global QA. Delegates to final-auditor agent."""
    cfg = load_config()
    max_iter = cfg.get("processing", {}).get("max_quality_iterations", 5)
    g_iter = state.get("global_iteration", 0) + 1
    state["global_iteration"] = g_iter

    if g_iter > max_iter:
        logger.warning("Global QA exceeded max iterations")
        return set_phase(state, "BLOCKED",
                         last_error="Global QA exceeded max iterations")

    return set_phase(state, "GLOBAL_QA",
                     global_iteration=g_iter,
                     agent_action="RUN_GLOBAL_QA")


def step_export(state: Dict[str, Any]) -> Dict[str, Any]:
    """Export final DOCX and PDF."""
    cfg = load_config()
    assembled = WORK_DIR / "assembled" / "merged.docx"

    if not assembled.exists():
        return set_error(state, "Assembled document not found for export")

    # Copy final DOCX
    doc_name = cfg.get("document", {}).get("name", "output.docx")
    final_docx = OUTPUT_DIR / doc_name
    shutil.copy2(str(assembled), str(final_docx))
    logger.info("Final DOCX: %s", final_docx)

    # Export PDF
    if cfg.get("output", {}).get("pdf", True):
        rc, out, err = run_script("export_pdf.py", str(final_docx))
        if rc != 0:
            logger.warning("PDF export failed: %s", err)

    state["last_successful_step"] = "EXPORT"
    return set_phase(state, "FINAL_REPORT")


def step_final_report(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate the final quality report."""
    rc, out, err = run_script("generate_report.py")
    if rc != 0:
        return set_error(state, f"Report generation failed: {err}")

    state["last_successful_step"] = "FINAL_REPORT"
    return set_phase(state, "DONE")


# ── State machine dispatch ────────────────────────────────────

STEP_MAP = {
    "INIT": step_init,
    "INSPECTION": step_inspection,
    "STRUCTURE_ANALYSIS": step_structure_analysis,
    "WAITING_FOR_HUMAN_VALIDATION": step_waiting_for_validation,
    "STRUCTURE_LOCKED": step_structure_locked,
    "CHAPTER_PROCESSING": step_chapter_processing,
    "CHAPTER_QA": step_chapter_qa,
    "TARGETED_CORRECTION": step_targeted_correction,
    "CHAPTER_VALIDATED": step_chapter_validated,
    "NEXT_CHAPTER": step_next_chapter,
    "ASSEMBLY": step_assembly,
    "GLOBAL_QA": step_global_qa,
    "EXPORT": step_export,
    "FINAL_REPORT": step_final_report,
}


def run_one_step(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute one step of the state machine."""
    phase = state.get("current_phase", "INIT")

    if phase in ("DONE", "BLOCKED", "FAILED"):
        logger.info("Workflow in terminal state: %s", phase)
        return state

    handler = STEP_MAP.get(phase)
    if not handler:
        return set_error(state, f"Unknown phase: {phase}")

    return handler(state)


# ── Commands ───────────────────────────────────────────────────

def cmd_status() -> None:
    """Print current loop status."""
    state = get_loop_state()
    ch_status = load_state("chapter_status")

    counts = {"VALIDATED": 0, "PROCESSING": 0, "QA": 0,
              "NOT_PROCESSED": 0, "PENDING_MANUAL": 0, "FAILED": 0}
    if ch_status:
        for ch in ch_status.get("chapters", []):
            s = ch.get("status", "NOT_PROCESSED")
            counts[s] = counts.get(s, 0) + 1

    current_ch = state.get("current_chapter")
    ch_title = "—"
    if current_ch and ch_status:
        for ch in ch_status.get("chapters", []):
            if ch["id"] == current_ch:
                ch_title = ch.get("title", "?")
                break

    print(f"""
╔══════════════════════════════════════════════════╗
║           DOCUMENT PROCESSING LOOP               ║
╠══════════════════════════════════════════════════╣
║ STATUS        : {state.get('status', '?'):<32s} ║
║ PHASE         : {state.get('current_phase', '?'):<32s} ║
║ CHAPTER       : {(current_ch or '—'):<32s} ║
║ CHAPTER TITLE : {ch_title[:32]:<32s} ║
║ ITERATION     : {str(state.get('iteration', 0)):<32s} ║
║ LAST STEP     : {(state.get('last_successful_step') or '—'):<32s} ║
║ LAST ERROR    : {(state.get('last_error') or 'none')[:32]:<32s} ║
╠══════════════════════════════════════════════════╣
║ CHAPTERS                                         ║
║   Validated     : {counts['VALIDATED']:<29d} ║
║   Processing    : {counts['PROCESSING'] + counts['QA']:<29d} ║
║   Pending       : {counts['NOT_PROCESSED']:<29d} ║
║   Manual review : {counts['PENDING_MANUAL']:<29d} ║
║   Failed        : {counts['FAILED']:<29d} ║
╚══════════════════════════════════════════════════╝
""")
    if state.get("agent_action"):
        print(f"  NEXT AGENT ACTION: {state['agent_action']}")


def cmd_run(max_steps: int = 1) -> None:
    """Run one or more steps of the state machine."""
    if not acquire_lock():
        print("ERROR: Could not acquire lock. Another loop may be running.")
        sys.exit(1)

    try:
        state = get_loop_state()

        for i in range(max_steps):
            old_phase = state.get("current_phase")
            state = run_one_step(state)
            new_phase = state.get("current_phase")

            if new_phase in ("DONE", "BLOCKED", "FAILED"):
                break

            # If phase didn't change (waiting), stop
            if old_phase == new_phase:
                break

            # If agent action needed, stop to let Claude act
            if state.get("agent_action"):
                break

        cmd_status()
    finally:
        release_lock()


def cmd_reset(force: bool = False) -> None:
    """Reset the workflow to INIT."""
    if not force:
        print("WARNING: This will reset the entire workflow.")
        print("Run with --force to confirm.")
        return

    for f in STATE_DIR.glob("*.json"):
        f.unlink()
    for d in [WORK_DIR / "inspection", WORK_DIR / "chapters",
              WORK_DIR / "qa", WORK_DIR / "assembled"]:
        if d.exists():
            shutil.rmtree(d)
            d.mkdir(parents=True)
    for f in OUTPUT_DIR.glob("*"):
        if f.name != ".gitkeep":
            f.unlink()

    log_event("WORKFLOW_RESET")
    print("Workflow reset to INIT.")


def cmd_validate(json_path: Optional[str] = None) -> None:
    """Mark the structure as validated (human-in-the-loop)."""
    proposal = load_state("structure_proposal")
    if not proposal:
        print("ERROR: No structure_proposal.json found. Run inspection first.")
        sys.exit(1)

    if json_path:
        with open(json_path, "r", encoding="utf-8") as fh:
            locked = json.load(fh)
    else:
        # Auto-validate from proposal (for testing or when human edits the proposal)
        locked = {
            "validated": True,
            "validated_at": now_iso(),
            "validated_by": "human",
            "sections": [],
        }
        for i, sec in enumerate(proposal.get("sections", [])):
            locked["sections"].append({
                "id": f"CH{i+1:02d}",
                "paragraph_id": sec.get("heading_id", ""),
                "title": sec.get("heading_text", ""),
                "level": sec.get("heading_level") or 1,
                "first_paragraph_id": sec.get("first_paragraph_id"),
                "last_paragraph_id": sec.get("last_paragraph_id"),
            })

    locked["validated"] = True
    locked["validated_at"] = now_iso()
    save_state("structure_locked", locked)
    log_event("STRUCTURE_VALIDATED", sections=len(locked.get("sections", [])))
    print(f"Structure validated with {len(locked.get('sections', []))} sections.")


def cmd_chapter_done(chapter_id: str, passed: bool) -> None:
    """Mark a chapter QA as passed or failed (called by agents)."""
    state = get_loop_state()

    if passed:
        update_chapter(chapter_id, status="VALIDATED")
        log_event("CHAPTER_QA_PASSED", chapter=chapter_id)
        state = set_phase(state, "NEXT_CHAPTER")
    else:
        ch_status = load_state("chapter_status")
        ch = None
        for c in ch_status.get("chapters", []):
            if c["id"] == chapter_id:
                ch = c
                break
        if ch:
            cfg = load_config()
            max_iter = cfg.get("processing", {}).get("max_quality_iterations", 5)
            if ch.get("iterations", 0) >= max_iter:
                update_chapter(chapter_id, status="PENDING_MANUAL")
                log_event("CHAPTER_PENDING_MANUAL", chapter=chapter_id)
                state = set_phase(state, "NEXT_CHAPTER")
            else:
                log_event("CHAPTER_QA_FAILED", chapter=chapter_id,
                          iteration=ch.get("iterations", 0))
                state = set_phase(state, "TARGETED_CORRECTION")


def cmd_global_qa_done(passed: bool) -> None:
    """Mark global QA as passed or failed."""
    state = get_loop_state()
    if passed:
        state = set_phase(state, "EXPORT")
    else:
        cfg = load_config()
        max_iter = cfg.get("processing", {}).get("max_quality_iterations", 5)
        if state.get("global_iteration", 0) >= max_iter:
            state = set_phase(state, "BLOCKED",
                              last_error="Global QA failed after max iterations")
        else:
            state = set_phase(state, "TARGETED_GLOBAL_CORRECTION",
                              agent_action="APPLY_GLOBAL_CORRECTION")


# ── CLI ────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Agentic Document Processing Loop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  status              Show current loop state
  run [--steps N]     Run N steps of the state machine (default: 1)
  resume              Alias for 'run' — resume from last state
  reset [--force]     Reset workflow to INIT
  validate [FILE]     Mark structure as validated
  chapter-done ID     Mark chapter QA passed  (--passed/--failed)
  global-qa-done      Mark global QA done     (--passed/--failed)
  inspect             Run inspection only
  analyze             Run structure analysis only
  assemble            Run assembly only
  export              Run export only
  report              Generate final report
        """,
    )
    parser.add_argument("command", nargs="?", default="status",
                        choices=["status", "run", "resume", "reset",
                                 "validate", "chapter-done", "global-qa-done",
                                 "inspect", "analyze", "assemble", "export", "report"])
    parser.add_argument("--steps", type=int, default=1, help="Steps to run")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--passed", action="store_true")
    parser.add_argument("--failed", action="store_true")
    parser.add_argument("--chapter", type=str, help="Chapter ID")
    parser.add_argument("--file", type=str, help="Path to validated structure JSON")
    parser.add_argument("args", nargs="*")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
    elif args.command in ("run", "resume"):
        cmd_run(max_steps=args.steps)
    elif args.command == "reset":
        cmd_reset(force=args.force)
    elif args.command == "validate":
        cmd_validate(json_path=args.file or (args.args[0] if args.args else None))
    elif args.command == "chapter-done":
        cid = args.chapter or (args.args[0] if args.args else None)
        if not cid:
            print("ERROR: --chapter ID required")
            return 1
        cmd_chapter_done(cid, passed=args.passed)
    elif args.command == "global-qa-done":
        cmd_global_qa_done(passed=args.passed)
    elif args.command == "inspect":
        state = get_loop_state()
        step_inspection(state)
    elif args.command == "analyze":
        state = get_loop_state()
        step_structure_analysis(state)
    elif args.command == "assemble":
        state = get_loop_state()
        step_assembly(state)
    elif args.command == "export":
        state = get_loop_state()
        step_export(state)
    elif args.command == "report":
        from generate_report import main as gen_main
        return gen_main()

    return 0


if __name__ == "__main__":
    sys.exit(main())
