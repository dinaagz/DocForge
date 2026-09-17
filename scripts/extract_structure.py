#!/usr/bin/env python3
"""
extract_structure.py — Extract document structure from the manifest
and produce a structure_proposal.json + readable Markdown report.

This script does NOT decide the final hierarchy.  It extracts raw
signals so that Claude (structure-analyst agent) can propose a
semantic hierarchy for human validation.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

from common import (
    WORK_DIR, get_logger, load_state, log_event, now_iso, save_state,
)

logger = get_logger("structure")


def extract(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Build a raw structure extract from the manifest."""
    headings = manifest.get("headings", [])
    paragraphs = manifest.get("paragraphs", [])

    # Group paragraphs into sections delimited by headings
    sections: List[Dict[str, Any]] = []
    current: Dict[str, Any] | None = None

    for p in paragraphs:
        if p["type"] in ("heading", "heuristic_heading"):
            if current:
                sections.append(current)
            current = {
                "heading_id": p["id"],
                "heading_text": p["text_preview"].strip(),
                "heading_style": p["style"],
                "heading_level": p.get("heading_level"),
                "heuristic": p["type"] == "heuristic_heading",
                "paragraph_count": 0,
                "char_count": 0,
                "first_paragraph_id": None,
                "last_paragraph_id": None,
            }
        elif current:
            current["paragraph_count"] += 1
            current["char_count"] += p["char_count"]
            if current["first_paragraph_id"] is None:
                current["first_paragraph_id"] = p["id"]
            current["last_paragraph_id"] = p["id"]
        # paragraphs before first heading go into a preamble
        elif current is None and p["type"] == "body":
            if not sections and not current:
                current = {
                    "heading_id": None,
                    "heading_text": "[PREAMBLE — content before first heading]",
                    "heading_style": None,
                    "heading_level": None,
                    "heuristic": False,
                    "paragraph_count": 1,
                    "char_count": p["char_count"],
                    "first_paragraph_id": p["id"],
                    "last_paragraph_id": p["id"],
                }
            elif current is None:
                pass
            else:
                current["paragraph_count"] += 1
                current["char_count"] += p["char_count"]
                current["last_paragraph_id"] = p["id"]

    if current:
        sections.append(current)

    proposal = {
        "extracted_at": now_iso(),
        "source": manifest.get("source_file", "unknown"),
        "total_sections_detected": len(sections),
        "sections": sections,
        "notes": [
            "This is a raw extraction. A semantic analysis by the structure-analyst agent is required.",
            "Sections marked heuristic=true were detected by bold-text heuristic, not by Word heading styles.",
            "heading_level=null means the level could not be determined from the style alone.",
        ],
    }
    return proposal


def write_markdown_report(proposal: Dict[str, Any], out_path: Path) -> None:
    """Write a human-readable Markdown report of the structure proposal."""
    lines = [
        "# Structure Extraction Report",
        "",
        f"**Source:** {proposal['source']}",
        f"**Extracted at:** {proposal['extracted_at']}",
        f"**Sections detected:** {proposal['total_sections_detected']}",
        "",
        "## Detected Sections",
        "",
        "| # | ID | Level | Heuristic | Heading Text | Paragraphs | Chars |",
        "|---|-----|-------|-----------|--------------|------------|-------|",
    ]
    for i, sec in enumerate(proposal["sections"], 1):
        hid = sec["heading_id"] or "—"
        lvl = sec["heading_level"] if sec["heading_level"] else "?"
        heur = "✓" if sec["heuristic"] else ""
        txt = (sec["heading_text"][:60] + "…") if len(sec["heading_text"]) > 60 else sec["heading_text"]
        lines.append(f"| {i} | {hid} | {lvl} | {heur} | {txt} | {sec['paragraph_count']} | {sec['char_count']} |")

    lines += [
        "",
        "## Notes",
        "",
    ]
    for n in proposal.get("notes", []):
        lines.append(f"- {n}")
    lines.append("")
    lines.append("---")
    lines.append("*This report is auto-generated. The structure-analyst agent will propose a semantic hierarchy for human validation.*")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    manifest = load_state("document_manifest")
    if not manifest:
        logger.error("document_manifest.json not found — run inspect_docx.py first")
        print(json.dumps({"error": "document_manifest.json not found"}))
        return 1

    proposal = extract(manifest)
    save_state("structure_proposal", proposal)

    md_path = WORK_DIR / "inspection" / "structure_proposal.md"
    write_markdown_report(proposal, md_path)

    log_event("STRUCTURE_EXTRACTED", sections=proposal["total_sections_detected"])
    logger.info("Extracted %d sections", proposal["total_sections_detected"])
    print(json.dumps({"status": "ok", "sections": proposal["total_sections_detected"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
