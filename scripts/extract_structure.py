#!/usr/bin/env python3
"""
extract_structure.py — Extract document structure from the manifest
and produce a structure_proposal.json + readable Markdown report.

This script extracts RAW DATA from the document: existing headings,
paragraph content, section sizes, and structural anomalies.  It does
NOT decide the final hierarchy.  The structure-analyst agent uses this
data to propose a COMPLETE RESTRUCTURING for human validation.

The existing document numbering and heading styles are treated as
INPUT SIGNALS, not as the target structure.
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

MAX_CONTENT_PREVIEW = 500  # chars of body text per section for semantic analysis


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
                "word_count": 0,
                "first_paragraph_id": None,
                "last_paragraph_id": None,
                "content_preview": "",
                "paragraph_ids": [],
            }
        elif current:
            current["paragraph_count"] += 1
            current["char_count"] += p["char_count"]
            current["word_count"] += len(p.get("text_preview", "").split())
            current["paragraph_ids"].append(p["id"])
            if current["first_paragraph_id"] is None:
                current["first_paragraph_id"] = p["id"]
            current["last_paragraph_id"] = p["id"]
            # Accumulate content preview for semantic analysis
            if len(current["content_preview"]) < MAX_CONTENT_PREVIEW:
                txt = p.get("text_preview", "").strip()
                if txt:
                    current["content_preview"] += " " + txt
        # paragraphs before first heading go into a preamble
        elif current is None and p["type"] == "body":
            if not sections and not current:
                current = {
                    "heading_id": None,
                    "heading_text": "[PREAMBLE]",
                    "heading_style": None,
                    "heading_level": None,
                    "heuristic": False,
                    "paragraph_count": 1,
                    "char_count": p["char_count"],
                    "word_count": len(p.get("text_preview", "").split()),
                    "first_paragraph_id": p["id"],
                    "last_paragraph_id": p["id"],
                    "content_preview": p.get("text_preview", "")[:MAX_CONTENT_PREVIEW],
                    "paragraph_ids": [p["id"]],
                }
            elif current is None:
                pass
            else:
                current["paragraph_count"] += 1
                current["char_count"] += p["char_count"]
                current["word_count"] += len(p.get("text_preview", "").split())
                current["paragraph_ids"].append(p["id"])
                current["last_paragraph_id"] = p["id"]

    if current:
        sections.append(current)

    # Trim content previews
    for sec in sections:
        sec["content_preview"] = sec["content_preview"][:MAX_CONTENT_PREVIEW].strip()

    # Detect structural anomalies for the agent
    anomalies = _detect_anomalies(sections, paragraphs)

    proposal = {
        "extracted_at": now_iso(),
        "source": manifest.get("source_file", "unknown"),
        "total_paragraphs": len(paragraphs),
        "total_characters": sum(p["char_count"] for p in paragraphs),
        "estimated_pages": manifest.get("statistics", {}).get("estimated_pages", 0),
        "total_sections_detected": len(sections),
        "sections": sections,
        "anomalies": anomalies,
        "status": "RAW_EXTRACTION",
        "needs_agent_analysis": True,
        "notes": [
            "RAW EXTRACTION ONLY — the structure-analyst agent must analyze this data and propose a COMPLETE RESTRUCTURING.",
            "The existing headings and numbering are input signals, NOT the target structure.",
            "Sections marked heuristic=true were detected by bold-text heuristic, not by Word heading styles.",
            "heading_level=null means the level could not be determined from the style alone.",
            "content_preview contains the first ~500 characters of each section for semantic analysis.",
            "The agent must propose new chapter boundaries, titles, and a proper heading hierarchy.",
        ],
    }
    return proposal


def _detect_anomalies(sections: List[Dict[str, Any]], paragraphs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Detect structural anomalies to guide restructuring."""
    anomalies: List[Dict[str, str]] = []

    # Check for level jumps (e.g., heading 1 -> heading 3)
    prev_level = None
    for sec in sections:
        lvl = sec.get("heading_level")
        if lvl and prev_level and lvl > prev_level + 1:
            anomalies.append({
                "type": "level_jump",
                "section": sec["heading_text"][:80],
                "detail": f"Level jumps from {prev_level} to {lvl}",
            })
        if lvl:
            prev_level = lvl

    # Check for very short sections (< 100 chars)
    for sec in sections:
        if sec["char_count"] < 100 and sec["heading_id"]:
            anomalies.append({
                "type": "tiny_section",
                "section": sec["heading_text"][:80],
                "detail": f"Only {sec['char_count']} characters — may need merging",
            })

    # Check for very long sections (> 20000 chars, ~10 pages)
    for sec in sections:
        if sec["char_count"] > 20000:
            anomalies.append({
                "type": "oversized_section",
                "section": sec["heading_text"][:80],
                "detail": f"{sec['char_count']} characters (~{sec['char_count']//2000} pages) — may need splitting",
            })

    # Check for inconsistent heading styles (mix of proper and heuristic)
    proper_count = sum(1 for s in sections if not s["heuristic"] and s["heading_id"])
    heuristic_count = sum(1 for s in sections if s["heuristic"])
    if proper_count > 0 and heuristic_count > 0:
        anomalies.append({
            "type": "mixed_heading_styles",
            "section": "global",
            "detail": f"{proper_count} styled headings + {heuristic_count} heuristic (bold) headings — inconsistent formatting",
        })

    # Check for duplicate heading texts
    texts = [s["heading_text"].strip().lower() for s in sections if s["heading_id"]]
    seen = set()
    for t in texts:
        if t in seen:
            anomalies.append({
                "type": "duplicate_heading",
                "section": t[:80],
                "detail": "Duplicate heading text detected",
            })
        seen.add(t)

    # Check for missing top-level structure
    level_1_count = sum(1 for s in sections if s.get("heading_level") == 1)
    if level_1_count == 0:
        anomalies.append({
            "type": "no_top_level",
            "section": "global",
            "detail": "No level-1 headings found — the document lacks clear top-level structure",
        })

    return anomalies


def write_markdown_report(proposal: Dict[str, Any], out_path: Path) -> None:
    """Write a human-readable Markdown report for the structure-analyst agent."""
    lines = [
        "# Raw Structure Extraction Report",
        "",
        "> **This is NOT the final structure proposal.** This is raw data extracted from the document.",
        "> The structure-analyst agent must analyze this data and propose a complete restructuring.",
        "> The existing numbering and heading hierarchy do NOT define the target structure.",
        "",
        f"**Source:** {proposal['source']}",
        f"**Extracted at:** {proposal['extracted_at']}",
        f"**Total paragraphs:** {proposal.get('total_paragraphs', '?')}",
        f"**Total characters:** {proposal.get('total_characters', '?')}",
        f"**Estimated pages:** {proposal.get('estimated_pages', '?')}",
        f"**Sections detected (as-is):** {proposal['total_sections_detected']}",
        "",
    ]

    # Anomalies section
    anomalies = proposal.get("anomalies", [])
    if anomalies:
        lines += [
            "## Structural Anomalies Detected",
            "",
        ]
        for a in anomalies:
            lines.append(f"- **{a['type']}**: {a['detail']} (in: {a['section']})")
        lines.append("")

    # Sections table
    lines += [
        "## Existing Sections (as found in document)",
        "",
        "| # | ID | Level | Heuristic | Heading Text | Paras | Chars | Words |",
        "|---|-----|-------|-----------|--------------|-------|-------|-------|",
    ]
    for i, sec in enumerate(proposal["sections"], 1):
        hid = sec["heading_id"] or "---"
        lvl = sec["heading_level"] if sec["heading_level"] else "?"
        heur = "Y" if sec["heuristic"] else ""
        txt = (sec["heading_text"][:60] + "...") if len(sec["heading_text"]) > 60 else sec["heading_text"]
        lines.append(f"| {i} | {hid} | {lvl} | {heur} | {txt} | {sec['paragraph_count']} | {sec['char_count']} | {sec.get('word_count', '?')} |")

    # Content previews for semantic analysis
    lines += [
        "",
        "## Content Previews (for semantic analysis)",
        "",
    ]
    for i, sec in enumerate(proposal["sections"], 1):
        preview = sec.get("content_preview", "").strip()
        if preview:
            lines.append(f"### Section {i}: {sec['heading_text'][:80]}")
            lines.append(f"> {preview[:300]}...")
            lines.append("")

    lines += [
        "",
        "---",
        "**NEXT STEP:** The structure-analyst agent must read this data and propose a COMPLETE restructuring:",
        "- Define new chapter boundaries based on content (ignore existing numbering)",
        "- Propose a clean heading hierarchy (Level 1 = parts/chapters, Level 2 = sections, etc.)",
        "- Ensure balanced chapter sizes (no 1-paragraph or 40-page chapters)",
        "- The human will validate the proposed structure before it is applied",
    ]

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
