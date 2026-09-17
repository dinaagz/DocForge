#!/usr/bin/env python3
"""
update_fields.py — Update TOC and other fields in a DOCX.

Inserts a Table of Contents based on heading styles.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from common import get_logger, load_config, log_event

logger = get_logger("fields")


def add_toc(doc: Document, levels: int = 3) -> None:
    """Insert a TOC field at the beginning of the document."""
    # Find the first heading or use the start
    insert_before = None
    for i, para in enumerate(doc.paragraphs):
        if para.style and para.style.name.startswith("Heading"):
            insert_before = i
            break

    # Create TOC field
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()

    fldChar_begin = OxmlElement("w:fldChar")
    fldChar_begin.set(qn("w:fldCharType"), "begin")
    run._r.append(fldChar_begin)

    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = f' TOC \\o "1-{levels}" \\h \\z \\u '
    run._r.append(instrText)

    fldChar_separate = OxmlElement("w:fldChar")
    fldChar_separate.set(qn("w:fldCharType"), "separate")
    run._r.append(fldChar_separate)

    # Placeholder text
    run2 = paragraph.add_run("[Table of Contents — update fields in Word to populate]")

    fldChar_end = OxmlElement("w:fldChar")
    fldChar_end.set(qn("w:fldCharType"), "end")
    run2._r.append(fldChar_end)

    # Move TOC to before first heading
    if insert_before is not None and insert_before > 0:
        body = doc.element.body
        ref = doc.paragraphs[insert_before]._element
        body.insert(list(body).index(ref), paragraph._element)

    logger.info("TOC field inserted (levels 1-%d)", levels)


def main() -> int:
    parser = argparse.ArgumentParser(description="Update fields / add TOC in DOCX")
    parser.add_argument("input", help="Path to DOCX")
    parser.add_argument("--output", help="Output path (default: overwrite)")
    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        logger.error("File not found: %s", inp)
        return 1

    cfg = load_config()
    toc_cfg = cfg.get("toc", {})

    doc = Document(str(inp))

    if toc_cfg.get("automatic", True):
        add_toc(doc, levels=toc_cfg.get("levels", 3))

    out = Path(args.output) if args.output else inp
    doc.save(str(out))

    log_event("FIELDS_UPDATED", output=str(out))
    print(json.dumps({"status": "ok", "output": str(out)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
