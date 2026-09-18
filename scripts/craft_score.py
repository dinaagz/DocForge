#!/usr/bin/env python3
"""
craft_score.py -- Compute the Document Visual Quality Score (DVQS).

Scores each visual/editorial dimension on a 0-4 scale.
The score is INTERNAL (for the controller), not user-facing.

Dimensions:
  typography, hierarchy, spacing, composition, density,
  consistency, tables, figures, pagination, human_finish

Output: JSON with dimension scores, weakest dimensions, and
recommended actions.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from docx import Document
from docx.shared import Pt

from common import (
    PROJECT_ROOT,
    get_logger,
    load_config,
    log_event,
    paragraph_id,
)

logger = get_logger("craft_score")

WPNS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

DESIGN_DIR_PATH = PROJECT_ROOT / ".docforge" / "model" / "design_direction.yaml"

# Maximum score per dimension
MAX_SCORE = 4


def _load_design_direction() -> Dict[str, Any]:
    if DESIGN_DIR_PATH.exists():
        import yaml
        with open(DESIGN_DIR_PATH, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    return {}


def _clamp(value: float, lo: float = 0.0, hi: float = 4.0) -> float:
    return max(lo, min(hi, value))


# -- Dimension scorers --------------------------------------------------------

def _score_typography(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Score typography consistency (0-4)."""
    expected_font = dd.get("typography", {}).get("body_family") or cfg.get("formatting", {}).get("font", {}).get("family", "Times New Roman")
    expected_size = dd.get("typography", {}).get("body_size_pt") or cfg.get("formatting", {}).get("font", {}).get("size", 12)

    penalties = 0.0
    actions: List[str] = []
    font_violations = 0
    size_violations = 0
    total_runs = 0

    for para in doc.paragraphs:
        style_name = para.style.name if para.style else ""
        if style_name.startswith("Heading"):
            continue
        for run in para.runs:
            if not run.text.strip():
                continue
            total_runs += 1
            if run.font.name and run.font.name != expected_font:
                font_violations += 1
            if run.font.size and abs(run.font.size.pt - expected_size) > 0.5:
                size_violations += 1

    if total_runs > 0:
        font_ratio = font_violations / total_runs
        size_ratio = size_violations / total_runs
        penalties += font_ratio * 2.0
        penalties += size_ratio * 1.5
        if font_ratio > 0.1:
            actions.append(f"Normalize fonts to {expected_font}")
        if size_ratio > 0.1:
            actions.append(f"Normalize body text size to {expected_size}pt")

    return _clamp(MAX_SCORE - penalties), actions


def _score_hierarchy(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Score heading hierarchy quality (0-4)."""
    penalties = 0.0
    actions: List[str] = []
    prev_level: Optional[int] = None
    level_jumps = 0
    heading_count = 0

    heading_sizes: Dict[int, List[float]] = defaultdict(list)

    for para in doc.paragraphs:
        style_name = para.style.name if para.style else ""
        if not style_name.startswith("Heading"):
            continue
        heading_count += 1
        m = re.search(r"\d+", style_name)
        level = int(m.group()) if m else 1

        if prev_level is not None and level > prev_level + 1:
            level_jumps += 1
        prev_level = level

        for run in para.runs:
            if run.font.size:
                heading_sizes[level].append(run.font.size.pt)

    if heading_count > 0:
        penalties += level_jumps * 1.0
        if level_jumps > 0:
            actions.append(f"Fix {level_jumps} heading level jump(s)")

    # Check size proportionality
    level_avg: Dict[int, float] = {}
    for level, sizes in heading_sizes.items():
        if sizes:
            level_avg[level] = sum(sizes) / len(sizes)

    sorted_levels = sorted(level_avg.keys())
    for i in range(len(sorted_levels) - 1):
        l1, l2 = sorted_levels[i], sorted_levels[i + 1]
        if level_avg[l1] <= level_avg[l2]:
            penalties += 1.0
            actions.append(f"H{l1} should be visually larger than H{l2}")

    if heading_count == 0:
        penalties += 2.0
        actions.append("Add heading hierarchy to structure the document")

    return _clamp(MAX_SCORE - penalties), actions


def _score_spacing(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Score spacing consistency (0-4)."""
    penalties = 0.0
    actions: List[str] = []

    heading_spacing: Dict[int, List[Optional[float]]] = defaultdict(list)
    for para in doc.paragraphs:
        style_name = para.style.name if para.style else ""
        if style_name.startswith("Heading"):
            m = re.search(r"\d+", style_name)
            level = int(m.group()) if m else 1
            pf = para.paragraph_format
            space_before = pf.space_before.pt if pf.space_before else None
            heading_spacing[level].append(space_before)

    for level, spacings in heading_spacing.items():
        defined = [s for s in spacings if s is not None]
        if defined and len(set(defined)) > 1:
            penalties += 0.8
            actions.append(f"Standardize spacing for Heading {level}")

    return _clamp(MAX_SCORE - penalties), actions


def _score_composition(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Score overall composition (margins, alignment) (0-4)."""
    from docx.shared import Cm
    penalties = 0.0
    actions: List[str] = []

    margins_cfg = cfg.get("formatting", {}).get("margins", {})
    for section in doc.sections:
        for side, attr in [("top_cm", "top_margin"), ("bottom_cm", "bottom_margin"),
                           ("left_cm", "left_margin"), ("right_cm", "right_margin")]:
            expected = Cm(margins_cfg.get(side, 2.5))
            actual = getattr(section, attr)
            if actual and abs(actual - expected) > Cm(0.2):
                penalties += 0.5
                actions.append(f"Fix {side.replace('_cm', '')} margin")

    return _clamp(MAX_SCORE - penalties), actions


def _score_density(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Score page density balance (0-4)."""
    penalties = 0.0
    actions: List[str] = []

    page_chars: List[int] = []
    current = 0
    chars_per_page = 2000

    for para in doc.paragraphs:
        current += len(para.text)
        pf = para.paragraph_format
        has_break = pf.page_break_before
        if not has_break:
            for run in para.runs:
                for elem in run._element.iter(f"{WPNS}br"):
                    if elem.get(f"{WPNS}type") == "page":
                        has_break = True
        if has_break:
            page_chars.append(current - len(para.text))
            current = len(para.text)
        if current >= chars_per_page:
            page_chars.append(current)
            current = 0
    if current > 0:
        page_chars.append(current)

    if len(page_chars) > 2:
        avg = sum(page_chars) / len(page_chars)
        low_pages = sum(1 for c in page_chars if c < avg * 0.3)
        high_pages = sum(1 for c in page_chars if c > avg * 1.5)
        imbalance = (low_pages + high_pages) / len(page_chars)
        penalties += imbalance * 3.0
        if low_pages > 0:
            actions.append(f"{low_pages} nearly empty page(s) detected")
        if high_pages > 0:
            actions.append(f"{high_pages} overly dense page(s) detected")

    return _clamp(MAX_SCORE - penalties), actions


def _score_consistency(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Score style consistency across document sections (0-4)."""
    penalties = 0.0
    actions: List[str] = []

    total = len(doc.paragraphs)
    if total < 6:
        return MAX_SCORE, actions

    third = total // 3
    section_fonts: List[Counter] = []
    for start, end in [(0, third), (third, 2 * third), (2 * third, total)]:
        fonts: Counter = Counter()
        for para in doc.paragraphs[start:end]:
            for run in para.runs:
                if run.font.name and run.text.strip():
                    fonts[run.font.name] += 1
        section_fonts.append(fonts)

    # Compare dominant fonts across sections
    tops = []
    for sf in section_fonts:
        if sf:
            tops.append(sf.most_common(1)[0][0])
    if len(set(tops)) > 1:
        penalties += 2.0
        actions.append("Font usage drifts across document sections")

    return _clamp(MAX_SCORE - penalties), actions


def _score_tables(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Score table quality (0-4). Returns MAX_SCORE if no tables."""
    if not doc.tables:
        return float(MAX_SCORE), []

    penalties = 0.0
    actions: List[str] = []

    for t_idx, table in enumerate(doc.tables):
        if len(table.rows) < 2:
            continue
        first_row = table.rows[0]
        has_header = any(
            run.bold
            for cell in first_row.cells
            for para in cell.paragraphs
            for run in para.runs
        )
        if not has_header:
            penalties += 0.5
            actions.append(f"Table {t_idx + 1}: add header row emphasis")

    return _clamp(MAX_SCORE - penalties), actions


def _score_figures(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Score figure treatment (0-4). Returns MAX_SCORE if no figures."""
    WPNS_WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
    image_paras: List[int] = []
    for idx, para in enumerate(doc.paragraphs):
        for run in para.runs:
            drawings = run._element.findall(f".//{WPNS_WP}inline") + run._element.findall(f".//{WPNS_WP}anchor")
            if drawings:
                image_paras.append(idx)
                break

    if not image_paras:
        return float(MAX_SCORE), []

    penalties = 0.0
    actions: List[str] = []
    for img_idx in image_paras:
        has_caption = False
        for check in range(max(0, img_idx - 2), min(len(doc.paragraphs), img_idx + 3)):
            if check == img_idx:
                continue
            cp = doc.paragraphs[check]
            style = cp.style.name if cp.style else ""
            text = cp.text.strip().lower()
            if "caption" in style.lower() or text.startswith(("figure", "fig.", "fig ")):
                has_caption = True
                break
        if not has_caption:
            penalties += 0.8
            actions.append(f"Figure near paragraph {img_idx}: missing caption")

    return _clamp(MAX_SCORE - penalties), actions


def _score_pagination(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Score pagination quality -- orphan headings, widow lines (0-4)."""
    penalties = 0.0
    actions: List[str] = []

    for idx, para in enumerate(doc.paragraphs):
        style_name = para.style.name if para.style else ""
        if not style_name.startswith("Heading"):
            continue

        # Check if heading is followed by a page break (orphan heading)
        if idx + 1 < len(doc.paragraphs):
            next_para = doc.paragraphs[idx + 1]
            pf = next_para.paragraph_format
            if pf.page_break_before:
                penalties += 0.8
                actions.append(f"Orphan heading at paragraph {idx}")

    return _clamp(MAX_SCORE - penalties), actions


def _score_human_finish(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Score human-like quality (0-4)."""
    penalties = 0.0
    actions: List[str] = []

    # Paragraph length uniformity
    body_lengths: List[int] = []
    for para in doc.paragraphs:
        style_name = para.style.name if para.style else ""
        if not style_name.startswith("Heading") and para.text.strip():
            wc = len(para.text.split())
            if wc > 5:
                body_lengths.append(wc)

    if len(body_lengths) > 10:
        avg = sum(body_lengths) / len(body_lengths)
        uniform = sum(1 for l in body_lengths if abs(l - avg) < 5)
        ratio = uniform / len(body_lengths)
        if ratio > 0.6:
            penalties += 1.5
            actions.append("Paragraph lengths are too uniform -- vary for natural rhythm")

    # Bold overuse
    bold_count = 0
    body_count = 0
    for para in doc.paragraphs:
        style_name = para.style.name if para.style else ""
        if style_name.startswith("Heading") or not para.text.strip():
            continue
        body_count += 1
        runs_with_text = [r for r in para.runs if r.text.strip()]
        if runs_with_text and all(r.bold for r in runs_with_text):
            bold_count += 1

    if body_count > 0 and bold_count / body_count > 0.3:
        penalties += 1.5
        actions.append("Bold overuse detected -- reduce to key terms only")

    return _clamp(MAX_SCORE - penalties), actions


# -- Orchestrator -------------------------------------------------------------

SCORERS = {
    "typography": _score_typography,
    "hierarchy": _score_hierarchy,
    "spacing": _score_spacing,
    "composition": _score_composition,
    "density": _score_density,
    "consistency": _score_consistency,
    "tables": _score_tables,
    "figures": _score_figures,
    "pagination": _score_pagination,
    "human_finish": _score_human_finish,
}


def score(docx_path: Path, cfg: Dict[str, Any], dd: Dict[str, Any]) -> Dict[str, Any]:
    """Compute the Document Visual Quality Score."""
    logger.info("Scoring %s", docx_path)
    doc = Document(str(docx_path))

    dimensions: Dict[str, Any] = {}
    all_actions: List[str] = []
    for name, scorer_fn in SCORERS.items():
        try:
            dim_score, actions = scorer_fn(doc, cfg, dd)
        except Exception as exc:
            logger.warning("Scorer %s failed: %s", name, exc)
            dim_score = 0.0
            actions = [f"Scorer {name} failed: {exc}"]
        dimensions[name] = round(dim_score, 2)
        all_actions.extend(actions)

    # Weakest dimensions (score < 3)
    weakest = sorted(
        [(name, s) for name, s in dimensions.items() if s < 3.0],
        key=lambda x: x[1],
    )

    result = {
        "dimensions": dimensions,
        "weakest": [{"dimension": name, "score": s} for name, s in weakest],
        "recommended_actions": all_actions,
    }

    logger.info("Scoring complete: %s", {k: v for k, v in dimensions.items()})
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute Document Visual Quality Score")
    parser.add_argument("input", help="Path to DOCX file")
    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        logger.error("File not found: %s", inp)
        return 1

    cfg = load_config()
    dd = _load_design_direction()
    result = score(inp, cfg, dd)

    log_event("CRAFT_SCORE", dimensions=result["dimensions"])
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
