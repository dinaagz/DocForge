#!/usr/bin/env python3
"""
validate_layout.py — Validate formatting compliance of a DOCX against config.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

from docx import Document
from docx.shared import Cm, Pt

from common import get_logger, load_config, log_event

logger = get_logger("validate_layout")


def validate(doc: Document, cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    fmt = cfg.get("formatting", {})
    expected_font = fmt.get("font", {}).get("family", "Times New Roman")
    expected_size = fmt.get("font", {}).get("size", 12)
    expected_spacing = fmt.get("paragraph", {}).get("line_spacing", 1.25)
    hdg_cfg = cfg.get("headings", {})

    for idx, para in enumerate(doc.paragraphs):
        pid = f"P{idx:06d}"
        style_name = para.style.name if para.style else ""
        is_heading = style_name.startswith("Heading")

        for run in para.runs:
            if not run.text.strip():
                continue
            # Check font family
            if run.font.name and run.font.name != expected_font:
                issues.append({
                    "paragraph_id": pid,
                    "criterion": "C3",
                    "issue": "wrong_font",
                    "expected": expected_font,
                    "found": run.font.name,
                })
            # Check font size
            if run.font.size:
                if is_heading:
                    m = re.search(r"\d+", style_name)
                    hnum = int(m.group()) if m else 1
                    h_cfg = hdg_cfg.get(f"heading_{hnum}", {})
                    exp_size = h_cfg.get("size", expected_size)
                else:
                    exp_size = expected_size

                if run.font.size != Pt(exp_size):
                    issues.append({
                        "paragraph_id": pid,
                        "criterion": "C3",
                        "issue": "wrong_font_size",
                        "expected_pt": exp_size,
                        "found_pt": run.font.size.pt if run.font.size else None,
                    })

    # Check margins
    margins_cfg = fmt.get("margins", {})
    for sec_idx, section in enumerate(doc.sections):
        for side, attr in [("top_cm", "top_margin"), ("bottom_cm", "bottom_margin"),
                           ("left_cm", "left_margin"), ("right_cm", "right_margin")]:
            expected = Cm(margins_cfg.get(side, 2.5))
            actual = getattr(section, attr)
            if actual and abs(actual - expected) > Cm(0.1):
                issues.append({
                    "section": sec_idx,
                    "criterion": "C3",
                    "issue": f"wrong_{side}",
                    "expected_cm": margins_cfg.get(side, 2.5),
                    "found_emu": actual,
                })

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate DOCX layout against config")
    parser.add_argument("input", help="Path to DOCX")
    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        logger.error("File not found: %s", inp)
        return 1

    cfg = load_config()
    doc = Document(str(inp))
    issues = validate(doc, cfg)

    log_event("LAYOUT_VALIDATION", issues_found=len(issues))
    result = {"status": "PASS" if not issues else "FAIL", "issues": len(issues), "details": issues}
    print(json.dumps(result, indent=2, default=str))
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
