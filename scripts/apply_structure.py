#!/usr/bin/env python3
"""
apply_structure.py — Apply the locked heading hierarchy to the DOCX.

Reads structure_locked.json and sets the Word heading styles on the
corresponding paragraphs. Does NOT touch body text.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict

from docx import Document
from docx.shared import Pt

from common import (
    INPUT_DIR, WORK_DIR, get_logger, input_docx, load_config,
    load_state, log_event, now_iso, save_state,
)

logger = get_logger("apply_structure")


def apply(docx_path: Path, locked: Dict[str, Any], cfg: Dict) -> Path:
    """Apply heading levels from locked structure; return path to new file."""
    doc = Document(str(docx_path))

    # Build a lookup: paragraph_index -> desired heading level
    heading_map: Dict[int, int] = {}
    for sec in locked.get("sections", []):
        pid = sec.get("paragraph_id", "")
        # Extract index from P000042 -> 42
        if not pid:
            continue
        m = re.match(r"P(\d+)", pid)
        if m:
            heading_map[int(m.group(1))] = sec.get("level", 1)

    changes = 0
    for idx, para in enumerate(doc.paragraphs):
        if idx in heading_map:
            level = heading_map[idx]
            style_name = f"Heading {level}"
            try:
                para.style = doc.styles[style_name]
                changes += 1
            except KeyError:
                logger.warning("Style %s not found in document; skipping para %d", style_name, idx)

    out_path = WORK_DIR / "assembled" / f"structured_{docx_path.name}"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))

    log_event("STRUCTURE_APPLIED", changes=changes, output=str(out_path))
    logger.info("Applied %d heading changes -> %s", changes, out_path)
    return out_path


def main() -> int:
    cfg = load_config()
    locked = load_state("structure_locked")
    if not locked:
        logger.error("structure_locked.json not found")
        print(json.dumps({"error": "structure_locked.json missing"}))
        return 1

    docx_path = input_docx(cfg)
    if not docx_path.exists():
        logger.error("Source DOCX not found: %s", docx_path)
        print(json.dumps({"error": f"File not found: {docx_path}"}))
        return 1

    out = apply(docx_path, locked, cfg)
    print(json.dumps({"status": "ok", "output": str(out)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
