"""Canonical document model — the true source of authority.

Built from extraction; rebuilt independently of the source document's
numbering. Any rebuild flows from here.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .events import emit, now_iso
from .paths import CANONICAL_PATH, INPUT_DIR, WORK_DIR, ensure_layout


def _hash_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def _hash_file(p: Path) -> str:
    if not p.exists():
        return ""
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def new_model() -> Dict[str, Any]:
    """Empty extended canonical model — full field set for any format."""
    return {
        "metadata": {
            "created_at": now_iso(),
            "source_path": None,
            "source_hash": "",
            "engine": "docforge",
            "version": "0.2.0",
            "document_format": "unknown",
        },
        "language": "fr",
        "document_type": "auto",
        "style_profile": "academic",
        "front_matter": [],
        # legacy DOCX-oriented fields (kept for retro-compat)
        "chapters": [],
        "paragraphs": [],
        "footnotes": [],
        "appendices": [],
        "cross_references": [],
        "corrections": [],
        # extended universal fields
        "sections": [],
        "blocks": [],
        "pages": [],
        "slides": [],
        "sheets": [],
        "tables": [],
        "figures": [],
        "images": [],
        "charts": [],
        "formulas": [],
        "equations": [],
        "headers": [],
        "footers": [],
        "styles": [],
        "references": [],
        "citations": [],
        "bibliography": [],
        "hyperlinks": [],
        "embedded_objects": [],
        "external_dependencies": [],
        "calculations": [],
        "accessibility": {"structure_present": False, "alt_text": []},
        "provenance": [],
        "issues": [],
        "issue_links": [],
        "verification_evidence": [],
    }


def load_canonical() -> Dict[str, Any]:
    if not CANONICAL_PATH.exists():
        return {}
    return json.loads(CANONICAL_PATH.read_text(encoding="utf-8"))


def save_canonical(model: Dict[str, Any]) -> None:
    ensure_layout()
    CANONICAL_PATH.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
    emit("CANONICAL_SAVED", chapters=len(model.get("chapters", [])),
         paragraphs=len(model.get("paragraphs", [])))


def build_from_inspection() -> Dict[str, Any]:
    """Read work/inspection/*.json and structure_proposal.json to build a
    canonical model. Numbering from the source is IGNORED — the rebuilt
    chapter hierarchy becomes the authority.
    """
    ensure_layout()
    insp = WORK_DIR / "inspection" / "paragraphs.json"
    if not insp.exists():
        insp = WORK_DIR / "inspection" / "document_manifest.json"
    struct = WORK_DIR / "inspection" / "structure_proposal.json"

    paragraphs: List[Dict[str, Any]] = []
    if insp.exists():
        try:
            data = json.loads(insp.read_text(encoding="utf-8"))
            src_paragraphs = data.get("paragraphs", data if isinstance(data, list) else [])
            for i, p in enumerate(src_paragraphs):
                text = p.get("text", "") if isinstance(p, dict) else str(p)
                paragraphs.append({
                    "id": f"P{i+1:06d}",
                    "type": "paragraph",
                    "content": text,
                    "parent_id": None,
                    "order": i,
                    "hash": _hash_str(text),
                    "confidence": 1.0,
                    "status": "extracted",
                })
        except json.JSONDecodeError:
            pass

    chapters: List[Dict[str, Any]] = []
    if struct.exists():
        try:
            data = json.loads(struct.read_text(encoding="utf-8"))
            src = data.get("restructured_sections") or data.get("sections") or []
            for i, s in enumerate(src):
                title = s.get("proposed_title") or s.get("heading_text") or f"Chapitre {i+1}"
                chapters.append({
                    "id": f"CH{i+1:02d}",
                    "title": title,
                    "level": 1,
                    "order": i,
                    "first_paragraph_id": s.get("first_paragraph_id"),
                    "last_paragraph_id": s.get("last_paragraph_id"),
                    "hash": _hash_str(title),
                    "confidence": s.get("confidence", 0.8),
                    "status": "proposed",
                })
        except json.JSONDecodeError:
            pass

    # Source hash (immutable)
    src_docx: Optional[Path] = None
    for p in INPUT_DIR.glob("*.docx"):
        src_docx = p
        break

    model = new_model()
    model["metadata"].update({
        "source_path": str(src_docx) if src_docx else None,
        "source_hash": _hash_file(src_docx) if src_docx else "",
    })
    model["chapters"] = chapters
    model["paragraphs"] = paragraphs
    save_canonical(model)
    return model
