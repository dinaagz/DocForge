#!/usr/bin/env python3
"""
craft_audit.py -- Audit a DOCX document for editorial craft quality.

Analyzes typography, spacing, density, hierarchy, tables, figures,
consistency, human finish, and anti-slop patterns.  Outputs JSON
with categorised issues.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from docx import Document
from docx.shared import Cm, Emu, Pt
from lxml import etree

from common import (
    PROJECT_ROOT,
    get_logger,
    load_config,
    log_event,
    paragraph_id,
)

logger = get_logger("craft_audit")

# -- XML namespaces -----------------------------------------------------------
WPNS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
WPNS_DRAWING = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
WPNS_WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"

# -- Design direction ---------------------------------------------------------
DESIGN_DIR_PATH = PROJECT_ROOT / ".docforge" / "model" / "design_direction.yaml"


def _load_design_direction() -> Dict[str, Any]:
    """Load design_direction.yaml, returning empty dict if missing."""
    if DESIGN_DIR_PATH.exists():
        import yaml
        with open(DESIGN_DIR_PATH, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    return {}


def _issue(
    category: str,
    severity: str,
    element_id: str,
    location: str,
    evidence: str,
    recommendation: str,
    confidence: float = 0.9,
) -> Dict[str, Any]:
    """Build a single issue dict."""
    return {
        "issue_id": f"CA-{uuid.uuid4().hex[:8].upper()}",
        "category": category,
        "severity": severity,
        "element_id": element_id,
        "location": location,
        "evidence": evidence,
        "recommendation": recommendation,
        "confidence": round(confidence, 2),
    }


# =============================================================================
# TYPOGRAPHY
# =============================================================================

def _audit_typography(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    expected_font = dd.get("typography", {}).get("body_family") or cfg.get("formatting", {}).get("font", {}).get("family", "Times New Roman")
    expected_size = dd.get("typography", {}).get("body_size_pt") or cfg.get("formatting", {}).get("font", {}).get("size", 12)

    font_counter: Counter = Counter()
    size_counter: Counter = Counter()

    for idx, para in enumerate(doc.paragraphs):
        pid = paragraph_id(idx)
        style_name = para.style.name if para.style else ""
        is_heading = style_name.startswith("Heading")

        for run in para.runs:
            if not run.text.strip():
                continue

            # Font consistency
            if run.font.name:
                font_counter[run.font.name] += 1
                if run.font.name != expected_font and not is_heading:
                    issues.append(_issue(
                        "TYPOGRAPHY", "HIGH", pid,
                        f"paragraph {idx}",
                        f"Font '{run.font.name}' found, expected '{expected_font}'",
                        f"Change font to '{expected_font}'",
                    ))

            # Size consistency (body text only)
            if run.font.size and not is_heading:
                size_pt = run.font.size.pt
                size_counter[size_pt] += 1
                if abs(size_pt - expected_size) > 0.5:
                    issues.append(_issue(
                        "TYPOGRAPHY", "MEDIUM", pid,
                        f"paragraph {idx}",
                        f"Font size {size_pt}pt found, expected {expected_size}pt",
                        f"Normalize body text to {expected_size}pt",
                    ))

            # Weight usage -- detect bold in body that is not emphasis
            if run.bold and not is_heading and len(run.text.strip()) > 80:
                issues.append(_issue(
                    "TYPOGRAPHY", "LOW", pid,
                    f"paragraph {idx}",
                    f"Long bold run ({len(run.text.strip())} chars) in body text",
                    "Reserve bold for short emphasis; use heading styles for section titles",
                    confidence=0.7,
                ))

    # Font inconsistency summary
    if len(font_counter) > 2:
        issues.append(_issue(
            "TYPOGRAPHY", "HIGH", "GLOBAL",
            "document",
            f"{len(font_counter)} different fonts used: {dict(font_counter.most_common(5))}",
            "Reduce to at most 2 font families (body + heading)",
        ))

    # Size inconsistency summary
    body_sizes = {s for s in size_counter if abs(s - expected_size) > 0.5}
    if len(body_sizes) > 2:
        issues.append(_issue(
            "TYPOGRAPHY", "MEDIUM", "GLOBAL",
            "document",
            f"Multiple unexpected body sizes: {sorted(body_sizes)}",
            f"Standardize body text to {expected_size}pt",
        ))

    return issues


# =============================================================================
# SPACING
# =============================================================================

def _audit_spacing(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    heading_spacing: Dict[int, List[Tuple[Optional[int], Optional[int]]]] = defaultdict(list)

    for idx, para in enumerate(doc.paragraphs):
        pid = paragraph_id(idx)
        style_name = para.style.name if para.style else ""
        pf = para.paragraph_format

        if style_name.startswith("Heading"):
            m = re.search(r"\d+", style_name)
            level = int(m.group()) if m else 1
            space_before = pf.space_before.pt if pf.space_before else None
            space_after = pf.space_after.pt if pf.space_after else None
            heading_spacing[level].append((space_before, space_after))

    # Check spacing consistency per heading level
    for level, spacings in heading_spacing.items():
        befores = [s[0] for s in spacings if s[0] is not None]
        afters = [s[1] for s in spacings if s[1] is not None]
        if befores and len(set(befores)) > 1:
            issues.append(_issue(
                "SPACING", "HIGH", f"Heading_{level}",
                f"heading level {level}",
                f"Inconsistent space-before values: {sorted(set(befores))}pt",
                f"Set uniform space-before for all Heading {level}",
            ))
        if afters and len(set(afters)) > 1:
            issues.append(_issue(
                "SPACING", "MEDIUM", f"Heading_{level}",
                f"heading level {level}",
                f"Inconsistent space-after values: {sorted(set(afters))}pt",
                f"Set uniform space-after for all Heading {level}",
            ))

    # Check for excessive paragraph gaps (double spacing between normal paras)
    prev_space_after = None
    for idx, para in enumerate(doc.paragraphs):
        pid = paragraph_id(idx)
        pf = para.paragraph_format
        style_name = para.style.name if para.style else ""
        if not style_name.startswith("Heading"):
            space_before = pf.space_before.pt if pf.space_before else None
            if space_before is not None and space_before > 24:
                issues.append(_issue(
                    "SPACING", "LOW", pid,
                    f"paragraph {idx}",
                    f"Excessive space-before ({space_before}pt) on body paragraph",
                    "Reduce spacing to maintain consistent visual rhythm",
                    confidence=0.7,
                ))

    return issues


# =============================================================================
# DENSITY
# =============================================================================

def _audit_density(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    target_density = dd.get("density", "medium")

    # Estimate per-page density by chunking paragraphs
    page_chars: List[int] = []
    current_page_chars = 0
    chars_per_page_estimate = 2000  # rough estimate

    for para in doc.paragraphs:
        char_count = len(para.text)
        current_page_chars += char_count

        # Check for explicit page breaks
        has_page_break = False
        for run in para.runs:
            for elem in run._element.iter(f"{WPNS}br"):
                if elem.get(f"{WPNS}type") == "page":
                    has_page_break = True

        pf = para.paragraph_format
        if pf.page_break_before or has_page_break:
            page_chars.append(current_page_chars - char_count)
            current_page_chars = char_count

        if current_page_chars >= chars_per_page_estimate:
            page_chars.append(current_page_chars)
            current_page_chars = 0

    if current_page_chars > 0:
        page_chars.append(current_page_chars)

    if not page_chars:
        return issues

    avg_density = sum(page_chars) / len(page_chars) if page_chars else 0

    for page_idx, chars in enumerate(page_chars):
        density_ratio = chars / chars_per_page_estimate if chars_per_page_estimate else 0
        if density_ratio < 0.3:
            issues.append(_issue(
                "DENSITY", "MEDIUM", f"PAGE_{page_idx + 1}",
                f"page ~{page_idx + 1}",
                f"Low density ({density_ratio:.1%} fill), only {chars} chars",
                "Consider merging with adjacent page or adding content",
                confidence=0.7,
            ))
        elif density_ratio > 1.3:
            issues.append(_issue(
                "DENSITY", "LOW", f"PAGE_{page_idx + 1}",
                f"page ~{page_idx + 1}",
                f"High density ({density_ratio:.1%} fill), {chars} chars",
                "Consider breaking into multiple pages for readability",
                confidence=0.6,
            ))

    # Density variation
    if len(page_chars) > 2:
        min_d = min(page_chars)
        max_d = max(page_chars)
        if max_d > 0 and min_d / max_d < 0.25:
            issues.append(_issue(
                "DENSITY", "MEDIUM", "GLOBAL",
                "document",
                f"High density variation: min={min_d} chars, max={max_d} chars per page",
                "Balance content distribution across pages",
            ))

    return issues


# =============================================================================
# HIERARCHY
# =============================================================================

def _audit_hierarchy(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    hdg_cfg = cfg.get("headings", {})
    prev_level: Optional[int] = None

    heading_sizes: Dict[int, List[float]] = defaultdict(list)

    for idx, para in enumerate(doc.paragraphs):
        pid = paragraph_id(idx)
        style_name = para.style.name if para.style else ""

        if not style_name.startswith("Heading"):
            continue

        m = re.search(r"\d+", style_name)
        level = int(m.group()) if m else 1

        # Level jump detection
        if prev_level is not None and level > prev_level + 1:
            issues.append(_issue(
                "HIERARCHY", "CRITICAL", pid,
                f"paragraph {idx}",
                f"Heading level jumps from H{prev_level} to H{level} (missing H{prev_level + 1})",
                f"Add intermediate H{prev_level + 1} heading or demote this to H{prev_level + 1}",
            ))
        prev_level = level

        # Collect sizes for proportionality check
        for run in para.runs:
            if run.font.size:
                heading_sizes[level].append(run.font.size.pt)

    # Size proportionality: higher levels should have larger sizes
    level_avg: Dict[int, float] = {}
    for level, sizes in heading_sizes.items():
        if sizes:
            level_avg[level] = sum(sizes) / len(sizes)

    sorted_levels = sorted(level_avg.keys())
    for i in range(len(sorted_levels) - 1):
        l1, l2 = sorted_levels[i], sorted_levels[i + 1]
        if level_avg[l1] <= level_avg[l2]:
            issues.append(_issue(
                "HIERARCHY", "HIGH", "GLOBAL",
                f"heading levels {l1}-{l2}",
                f"H{l1} avg size ({level_avg[l1]:.1f}pt) is not larger than H{l2} ({level_avg[l2]:.1f}pt)",
                f"Ensure H{l1} is visually larger than H{l2}",
            ))

    return issues


# =============================================================================
# TABLES
# =============================================================================

def _audit_tables(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    table_style_cfg = dd.get("table_style", {})

    for t_idx, table in enumerate(doc.tables):
        tid = f"TABLE_{t_idx + 1}"

        # Header row presence
        if len(table.rows) > 1:
            first_row = table.rows[0]
            has_bold_header = False
            for cell in first_row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        if run.bold:
                            has_bold_header = True
                            break

            if not has_bold_header:
                issues.append(_issue(
                    "TABLES", "MEDIUM", tid,
                    f"table {t_idx + 1}",
                    "Table appears to have no visually distinct header row",
                    "Add bold or shading to the header row",
                    confidence=0.75,
                ))

        # Check for empty cells (potential alignment/padding issue)
        empty_cells = 0
        total_cells = 0
        for row in table.rows:
            for cell in row.cells:
                total_cells += 1
                if not cell.text.strip():
                    empty_cells += 1
        if total_cells > 0 and empty_cells / total_cells > 0.3:
            issues.append(_issue(
                "TABLES", "LOW", tid,
                f"table {t_idx + 1}",
                f"{empty_cells}/{total_cells} cells are empty ({empty_cells / total_cells:.0%})",
                "Review table for unnecessary empty cells",
                confidence=0.6,
            ))

        # Column count consistency
        col_counts = [len(row.cells) for row in table.rows]
        if len(set(col_counts)) > 1:
            issues.append(_issue(
                "TABLES", "HIGH", tid,
                f"table {t_idx + 1}",
                f"Inconsistent column counts across rows: {sorted(set(col_counts))}",
                "Ensure all rows have the same number of columns or use proper merging",
            ))

    return issues


# =============================================================================
# FIGURES
# =============================================================================

def _audit_figures(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    figure_cfg = dd.get("figure_style", {})
    caption_position = figure_cfg.get("caption_position", "below")

    # Track image positions and look for captions
    image_paragraphs: List[int] = []
    for idx, para in enumerate(doc.paragraphs):
        # Check if paragraph contains an image
        has_image = False
        for run in para.runs:
            drawing_elems = run._element.findall(f".//{WPNS_WP}inline") + run._element.findall(f".//{WPNS_WP}anchor")
            if drawing_elems:
                has_image = True
                break
        if has_image:
            image_paragraphs.append(idx)

    for img_idx in image_paragraphs:
        pid = paragraph_id(img_idx)

        # Check for caption proximity
        has_caption = False
        caption_check_range = range(
            max(0, img_idx - 2),
            min(len(doc.paragraphs), img_idx + 3),
        )
        for check_idx in caption_check_range:
            if check_idx == img_idx:
                continue
            check_para = doc.paragraphs[check_idx]
            style = check_para.style.name if check_para.style else ""
            text = check_para.text.strip().lower()
            if "caption" in style.lower() or text.startswith(("figure", "fig.", "fig ")):
                has_caption = True
                break

        if not has_caption:
            issues.append(_issue(
                "FIGURES", "HIGH", pid,
                f"paragraph {img_idx}",
                "Figure without a detectable caption nearby",
                "Add a caption below the figure using the Caption style",
            ))

    return issues


# =============================================================================
# CONSISTENCY
# =============================================================================

def _audit_consistency(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []

    # Split document into thirds and check style drift
    total = len(doc.paragraphs)
    if total < 9:
        return issues

    third = total // 3
    sections = [
        doc.paragraphs[:third],
        doc.paragraphs[third:2 * third],
        doc.paragraphs[2 * third:],
    ]

    for section_label, section_name in enumerate(["first_third", "middle_third", "last_third"]):
        section = sections[section_label]
        fonts: Counter = Counter()
        sizes: Counter = Counter()
        for para in section:
            for run in para.runs:
                if not run.text.strip():
                    continue
                if run.font.name:
                    fonts[run.font.name] += 1
                if run.font.size:
                    sizes[run.font.size.pt] += 1

        if section_label > 0:
            prev_section = sections[section_label - 1]
            prev_fonts: Counter = Counter()
            for para in prev_section:
                for run in para.runs:
                    if run.font.name and run.text.strip():
                        prev_fonts[run.font.name] += 1

            # Check if dominant font changed
            if fonts and prev_fonts:
                curr_top = fonts.most_common(1)[0][0] if fonts else None
                prev_top = prev_fonts.most_common(1)[0][0] if prev_fonts else None
                if curr_top and prev_top and curr_top != prev_top:
                    issues.append(_issue(
                        "CONSISTENCY", "HIGH", "GLOBAL",
                        f"{section_name}",
                        f"Dominant font shifts from '{prev_top}' to '{curr_top}'",
                        "Ensure consistent font usage across the entire document",
                    ))

    return issues


# =============================================================================
# HUMAN_FINISH
# =============================================================================

def _audit_human_finish(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []

    # Detect uniform paragraph length (AI tell)
    body_lengths: List[int] = []
    for para in doc.paragraphs:
        style_name = para.style.name if para.style else ""
        if not style_name.startswith("Heading") and para.text.strip():
            word_count = len(para.text.split())
            if word_count > 5:
                body_lengths.append(word_count)

    if len(body_lengths) > 10:
        avg_len = sum(body_lengths) / len(body_lengths)
        uniform_count = sum(1 for l in body_lengths if abs(l - avg_len) < 5)
        uniform_ratio = uniform_count / len(body_lengths)
        if uniform_ratio > 0.6:
            issues.append(_issue(
                "HUMAN_FINISH", "MEDIUM", "GLOBAL",
                "document",
                f"{uniform_ratio:.0%} of paragraphs within 5 words of mean length ({avg_len:.0f} words)",
                "Vary paragraph length for natural rhythm",
                confidence=0.8,
            ))

    # Detect bold overuse
    bold_para_count = 0
    total_body_paras = 0
    for para in doc.paragraphs:
        style_name = para.style.name if para.style else ""
        if style_name.startswith("Heading") or not para.text.strip():
            continue
        total_body_paras += 1
        runs_with_text = [r for r in para.runs if r.text.strip()]
        if runs_with_text and all(r.bold for r in runs_with_text):
            bold_para_count += 1

    if total_body_paras > 0:
        bold_ratio = bold_para_count / total_body_paras
        if bold_ratio > 0.3:
            issues.append(_issue(
                "HUMAN_FINISH", "HIGH", "GLOBAL",
                "document",
                f"{bold_ratio:.0%} of body paragraphs are fully bold ({bold_para_count}/{total_body_paras})",
                "Reduce bold usage; reserve for key terms and short emphasis only",
            ))

    # Detect repetitive sentence starters
    starters: Counter = Counter()
    for para in doc.paragraphs:
        text = para.text.strip()
        if text and len(text.split()) > 5:
            first_words = " ".join(text.split()[:3]).lower()
            starters[first_words] += 1

    for starter, count in starters.most_common(5):
        if count > 5:
            issues.append(_issue(
                "HUMAN_FINISH", "LOW", "GLOBAL",
                "document",
                f"Repetitive sentence starter '{starter}' appears {count} times",
                "Vary sentence openings for more natural writing",
                confidence=0.7,
            ))

    return issues


# =============================================================================
# ANTI_SLOP
# =============================================================================

def _audit_anti_slop(doc: Document, cfg: Dict[str, Any], dd: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    full_text = "\n".join(p.text for p in doc.paragraphs)
    total_words = len(full_text.split())
    if total_words == 0:
        return issues

    # Em-dash frequency
    em_dash_count = full_text.count("—") + full_text.count("–")
    em_dash_per_1000 = (em_dash_count / total_words) * 1000
    if em_dash_per_1000 > 5:
        issues.append(_issue(
            "ANTI_SLOP", "MEDIUM", "GLOBAL",
            "document",
            f"High em/en-dash frequency: {em_dash_count} dashes ({em_dash_per_1000:.1f} per 1000 words)",
            "Reduce dash usage; use commas, semicolons, or restructure sentences",
        ))

    # Filler word detection
    filler_patterns = [
        r"\bnotamment\b", r"\ben effet\b", r"\bainsi\b",
        r"\bbasically\b", r"\bessentially\b", r"\bfundamentally\b",
        r"\bin order to\b", r"\bit is important to note\b",
        r"\bit should be noted\b", r"\bneedless to say\b",
    ]
    for pattern in filler_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if len(matches) > 8:
            issues.append(_issue(
                "ANTI_SLOP", "LOW", "GLOBAL",
                "document",
                f"Filler phrase '{matches[0]}' appears {len(matches)} times",
                "Reduce filler phrases for tighter prose",
                confidence=0.6,
            ))

    # Generic placeholder detection
    placeholder_patterns = [
        r"\b[Xx]{3,}\b", r"\bTODO\b", r"\bXXX\b",
        r"\bLorem ipsum\b", r"\b\[INSERT\b", r"\bTBD\b",
    ]
    for pattern in placeholder_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            issues.append(_issue(
                "ANTI_SLOP", "CRITICAL", "GLOBAL",
                "document",
                f"Placeholder text detected: '{matches[0]}' ({len(matches)} occurrences)",
                "Replace all placeholder text with final content",
            ))

    return issues


# =============================================================================
# Main audit orchestrator
# =============================================================================

AUDIT_FUNCTIONS = [
    _audit_typography,
    _audit_spacing,
    _audit_density,
    _audit_hierarchy,
    _audit_tables,
    _audit_figures,
    _audit_consistency,
    _audit_human_finish,
    _audit_anti_slop,
]


def audit(docx_path: Path, cfg: Dict[str, Any], dd: Dict[str, Any]) -> Dict[str, Any]:
    """Run the full craft audit on a DOCX file."""
    logger.info("Starting craft audit on %s", docx_path)
    doc = Document(str(docx_path))

    all_issues: List[Dict[str, Any]] = []
    for audit_fn in AUDIT_FUNCTIONS:
        try:
            issues = audit_fn(doc, cfg, dd)
            all_issues.extend(issues)
        except Exception as exc:
            logger.warning("Audit function %s failed: %s", audit_fn.__name__, exc)
            all_issues.append(_issue(
                "INTERNAL", "LOW", "GLOBAL",
                "audit",
                f"Audit function {audit_fn.__name__} failed: {exc}",
                "Re-run audit after fixing the document",
                confidence=0.5,
            ))

    # Summarize by category and severity
    by_category: Dict[str, int] = Counter()
    by_severity: Dict[str, int] = Counter()
    for issue in all_issues:
        by_category[issue["category"]] += 1
        by_severity[issue["severity"]] += 1

    result = {
        "status": "PASS" if not all_issues else "FAIL",
        "total_issues": len(all_issues),
        "by_category": dict(by_category),
        "by_severity": dict(by_severity),
        "issues": all_issues,
    }

    logger.info("Craft audit complete: %d issues found", len(all_issues))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit DOCX for editorial craft quality")
    parser.add_argument("input", help="Path to DOCX file")
    parser.add_argument("--category", type=str, default=None,
                        help="Run only a specific audit category (e.g. TYPOGRAPHY, HIERARCHY, RHYTHM, HUMAN_FINISH, ANTI_SLOP, EDITORIAL_TASTE, POLISH)")
    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        logger.error("File not found: %s", inp)
        return 1

    cfg = load_config()
    dd = _load_design_direction()
    result = audit(inp, cfg, dd)

    if args.category:
        cat = args.category.upper()
        result["issues"] = [i for i in result["issues"] if i.get("category", "").upper() == cat]
        result["total_issues"] = len(result["issues"])
        result["status"] = "PASS" if not result["issues"] else "FAIL"

    log_event("CRAFT_AUDIT", issues_found=result["total_issues"])
    print(json.dumps(result, indent=2, default=str))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
