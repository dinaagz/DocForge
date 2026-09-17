#!/usr/bin/env python3
"""
check_unicode.py — Detect invisible / suspicious Unicode characters in a DOCX.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List

from docx import Document

from common import get_logger, log_event, paragraph_id

logger = get_logger("unicode")

# Characters that should not appear in normal French academic text
SUSPICIOUS = re.compile(
    r"[​‌‍‎‏"  # zero-width
    r"­"  # soft hyphen
    r"  "  # line/paragraph separators
    r"﻿"  # BOM
    r"￹￺￻"  # interlinear annotation
    r"‪-‮"  # bidi overrides
    r"⁦-⁩"  # bidi isolates
    r"]"
)


def check(doc: Document) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for idx, para in enumerate(doc.paragraphs):
        for m in SUSPICIOUS.finditer(para.text):
            char = m.group()
            issues.append({
                "paragraph_id": paragraph_id(idx),
                "position": m.start(),
                "character": repr(char),
                "codepoint": f"U+{ord(char):04X}",
                "name": unicodedata.name(char, "UNKNOWN"),
                "context": para.text[max(0, m.start()-20):m.start()+20],
            })
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check for suspicious Unicode in DOCX")
    parser.add_argument("input", help="Path to DOCX")
    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        logger.error("File not found: %s", inp)
        return 1

    doc = Document(str(inp))
    issues = check(doc)

    log_event("UNICODE_CHECK", issues_found=len(issues))
    print(json.dumps({"status": "ok", "issues": len(issues), "details": issues}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
