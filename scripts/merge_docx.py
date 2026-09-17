#!/usr/bin/env python3
"""
merge_docx.py — Merge processed chapters back into one DOCX.

Uses the locked structure to order chapters and rebuilds the
complete document with proper section breaks.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from common import (
    WORK_DIR, OUTPUT_DIR, get_logger, load_config, load_state,
    log_event, now_iso,
)

logger = get_logger("merge")


def merge_chapters(chapter_files: List[Path], output_path: Path) -> int:
    """Merge chapter DOCX files in order. Return paragraph count."""
    if not chapter_files:
        logger.error("No chapter files to merge")
        return 0

    # Start with first chapter
    merged = Document(str(chapter_files[0]))

    for cf in chapter_files[1:]:
        sub = Document(str(cf))
        for para in sub.paragraphs:
            new_para = merged.add_paragraph()
            new_para.style = para.style
            new_para.alignment = para.alignment
            if para.paragraph_format.page_break_before:
                new_para.paragraph_format.page_break_before = True

            for run in para.runs:
                new_run = new_para.add_run(run.text)
                new_run.bold = run.bold
                new_run.italic = run.italic
                new_run.underline = run.underline
                if run.font.name:
                    new_run.font.name = run.font.name
                if run.font.size:
                    new_run.font.size = run.font.size
                if run.font.color and run.font.color.rgb:
                    new_run.font.color.rgb = run.font.color.rgb

    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.save(str(output_path))
    total = len(merged.paragraphs)
    logger.info("Merged %d files -> %s (%d paragraphs)", len(chapter_files), output_path, total)
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge chapter DOCX files")
    parser.add_argument("--chapters-dir", type=str,
                        default=str(WORK_DIR / "chapters"),
                        help="Directory containing chapter DOCX files")
    parser.add_argument("--output", type=str,
                        default=str(WORK_DIR / "assembled" / "merged.docx"),
                        help="Output merged DOCX path")
    args = parser.parse_args()

    chapters_dir = Path(args.chapters_dir)
    if not chapters_dir.exists():
        logger.error("Chapters directory not found: %s", chapters_dir)
        return 1

    # Load chapter status to get correct order
    ch_status = load_state("chapter_status")
    chapter_ids = [c["id"] for c in ch_status.get("chapters", [])]

    chapter_files: List[Path] = []
    for cid in chapter_ids:
        cf = chapters_dir / f"{cid}.docx"
        if cf.exists():
            chapter_files.append(cf)
        else:
            logger.warning("Chapter file missing: %s", cf)

    if not chapter_files:
        # Fallback: glob sorted
        chapter_files = sorted(chapters_dir.glob("*.docx"))

    out = Path(args.output)
    total = merge_chapters(chapter_files, out)

    log_event("CHAPTERS_MERGED", count=len(chapter_files), paragraphs=total, output=str(out))
    print(json.dumps({"status": "ok", "merged": len(chapter_files),
                       "paragraphs": total, "output": str(out)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
