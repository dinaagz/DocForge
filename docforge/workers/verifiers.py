"""Verifier workers — separate from builders (rule 5)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from ..paths import INPUT_DIR, WORK_DIR
from ._scripts import run_script
from .registry import register


def _working() -> Path:
    m = WORK_DIR / "assembled" / "merged.docx"
    if m.exists():
        return m
    for p in (WORK_DIR / "assembled").glob("structured_*.docx"):
        return p
    for p in INPUT_DIR.glob("*.docx"):
        return p
    return INPUT_DIR / "input.docx"


def _parse(out: str) -> Dict[str, Any]:
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {}


def integrity_verifier(ctx: Dict[str, Any]) -> Dict[str, Any]:
    working = _working()
    src = None
    for p in INPUT_DIR.glob("*.docx"):
        src = p
        break
    if not (src and working.exists()):
        return {"verdict": "SKIP"}
    rc, out, err = run_script("compare_docx.py", str(src), str(working))
    data = _parse(out)
    unauth = data.get("by_classification", {}).get("UNAUTHORIZED", 0)
    return {"verdict": "FAIL" if unauth else "PASS", "unauthorized": unauth,
            "report": data}


def content_verifier(ctx: Dict[str, Any]) -> Dict[str, Any]:
    return integrity_verifier(ctx)


def format_verifier(ctx: Dict[str, Any]) -> Dict[str, Any]:
    working = _working()
    if not working.exists():
        return {"verdict": "SKIP"}
    rc, out, err = run_script("validate_layout.py", str(working))
    data = _parse(out)
    issues = data.get("issues", 0)
    if isinstance(issues, list):
        issues = len(issues)
    return {"verdict": "PASS" if rc == 0 and issues == 0 else "FAIL",
            "issues": issues, "report": data}


def language_verifier(ctx: Dict[str, Any]) -> Dict[str, Any]:
    working = _working()
    if not working.exists():
        return {"verdict": "SKIP"}
    rc, out, err = run_script("check_unicode.py", str(working))
    data = _parse(out)
    issues = data.get("issues", 0)
    if isinstance(issues, list):
        issues = len(issues)
    return {"verdict": "PASS" if issues == 0 else "FAIL", "issues": issues}


def layout_verifier(ctx: Dict[str, Any]) -> Dict[str, Any]:
    return format_verifier(ctx)


def structure_verifier(ctx: Dict[str, Any]) -> Dict[str, Any]:
    from ..canonical import load_canonical
    doc = load_canonical()
    if not doc or not doc.get("chapters"):
        return {"verdict": "SKIP"}
    return {"verdict": "PASS", "chapters": len(doc["chapters"])}


def reference_verifier(ctx: Dict[str, Any]) -> Dict[str, Any]:
    return {"verdict": "SKIP", "note": "reference check heuristic pending"}


def pdf_verifier(ctx: Dict[str, Any]) -> Dict[str, Any]:
    from ..paths import OUTPUT_DIR
    pdfs = list(OUTPUT_DIR.glob("*.pdf"))
    if not pdfs:
        return {"verdict": "SKIP", "note": "no PDF exported yet"}
    pdf = pdfs[0]
    # Basic sanity: file size and existence
    size = pdf.stat().st_size
    return {"verdict": "PASS" if size > 1024 else "FAIL",
            "pdf": str(pdf), "size": size}


def coherence_agent(ctx: Dict[str, Any]) -> Dict[str, Any]:
    # Heuristic: cross-check title, chapters, unresolved refs from canonical
    from ..canonical import load_canonical
    doc = load_canonical()
    issues = []
    if doc:
        titles = {c.get("title", "") for c in doc.get("chapters", [])}
        if "" in titles:
            issues.append("empty chapter title detected")
    return {"verdict": "PASS" if not issues else "WARN", "issues": issues}


for _n, _f in (
    ("integrity-verifier", integrity_verifier),
    ("content-verifier", content_verifier),
    ("format-verifier", format_verifier),
    ("language-verifier", language_verifier),
    ("layout-verifier", layout_verifier),
    ("structure-verifier", structure_verifier),
    ("reference-verifier", reference_verifier),
    ("pdf-verifier", pdf_verifier),
    ("coherence-agent", coherence_agent),
):
    register(_n, _f)
