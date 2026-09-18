"""Builder workers — extraction, structure, formatting, assembly, export.

Each worker is a small Python callable. They wrap the existing scripts
so we preserve every proven deterministic tool.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict

from ..memory import correction, record
from ..paths import INPUT_DIR, OUTPUT_DIR, WORK_DIR
from ._scripts import run_script
from .registry import register


def _current_working_docx() -> Path:
    assembled = WORK_DIR / "assembled" / "merged.docx"
    if assembled.exists():
        return assembled
    for p in (WORK_DIR / "assembled").glob("structured_*.docx"):
        return p
    for p in INPUT_DIR.glob("*.docx"):
        return p
    return INPUT_DIR / "input.docx"


def extractor(ctx: Dict[str, Any]) -> Dict[str, Any]:
    rc, out, err = run_script("inspect_docx.py")
    return {"rc": rc, "stderr": err.strip(), "stdout": out[:400]}


def structure_architect(ctx: Dict[str, Any]) -> Dict[str, Any]:
    rc, out, err = run_script("extract_structure.py")
    return {"rc": rc, "stderr": err.strip()}


def structure_applier(ctx: Dict[str, Any]) -> Dict[str, Any]:
    rc, out, err = run_script("apply_structure.py")
    return {"rc": rc, "stderr": err.strip()}


def manifest_builder(ctx: Dict[str, Any]) -> Dict[str, Any]:
    rc, out, err = run_script("create_manifest.py")
    return {"rc": rc, "stderr": err.strip()}


def formatting_agent(ctx: Dict[str, Any]) -> Dict[str, Any]:
    target = Path(ctx.get("target") or _current_working_docx())
    if not target.exists():
        return {"skipped": "no target", "target": str(target)}
    rc, out, err = run_script("apply_styles.py", str(target))
    correction(target=str(target), before="raw", after="styled",
               agent="formatting-agent", rationale="apply document profile")
    return {"rc": rc, "target": str(target), "stderr": err.strip()}


def language_editor(ctx: Dict[str, Any]) -> Dict[str, Any]:
    target = Path(ctx.get("target") or _current_working_docx())
    rc, out, err = run_script("language_diff.py", str(target))
    return {"rc": rc, "stderr": err.strip(), "diff": out[:400]}


def document_builder(ctx: Dict[str, Any]) -> Dict[str, Any]:
    rc, out, err = run_script("merge_docx.py")
    return {"rc": rc, "stderr": err.strip()}


def assembler(ctx: Dict[str, Any]) -> Dict[str, Any]:
    merged = WORK_DIR / "assembled" / "merged.docx"
    if not merged.exists():
        # Fallback: use structured as assembled
        for p in (WORK_DIR / "assembled").glob("structured_*.docx"):
            shutil.copy2(p, merged)
            break
    run_script("apply_styles.py", str(merged)) if merged.exists() else None
    run_script("update_fields.py", str(merged)) if merged.exists() else None
    return {"assembled": str(merged), "exists": merged.exists()}


def exporter(ctx: Dict[str, Any]) -> Dict[str, Any]:
    merged = WORK_DIR / "assembled" / "merged.docx"
    if not merged.exists():
        return {"error": "no assembled document"}
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    final = OUTPUT_DIR / merged.name
    shutil.copy2(merged, final)
    pdf_rc, _, err = run_script("export_pdf.py", str(final))
    return {"docx": str(final), "pdf_rc": pdf_rc, "pdf_stderr": err.strip()}


def report_agent(ctx: Dict[str, Any]) -> Dict[str, Any]:
    from ..report import build_report
    docx, jsonp = build_report()
    return {"report_md": str(docx), "report_json": str(jsonp)}


# ── Register ─────────────────────────────────────────────
for _name, _fn in (
    ("extractor", extractor),
    ("document-analyst", extractor),
    ("structure-architect", structure_architect),
    ("structure-applier", structure_applier),
    ("manifest-builder", manifest_builder),
    ("formatting-agent", formatting_agent),
    ("layout-agent", formatting_agent),
    ("language-editor", language_editor),
    ("style-editor", language_editor),
    ("document-builder", document_builder),
    ("assembler", assembler),
    ("exporter", exporter),
    ("report-agent", report_agent),
):
    register(_name, _fn)
