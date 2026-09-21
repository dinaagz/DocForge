"""Audit Engine — produces Issue objects from a canonical document.

Content-agnostic first pass. Format-specific inspections are added by
plugging further audit callables via `register_probe`. Every call is
side-effect-free until `run_audit(..., persist=True)` is used.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, List

from ..events import emit
from .issues import Issue, save_all

Probe = Callable[[Dict[str, Any]], List[Issue]]

_PROBES: List[Probe] = []


def register_probe(fn: Probe) -> None:
    _PROBES.append(fn)


# ── built-in probes ───────────────────────────────────────────

def _probe_metadata(model: Dict[str, Any]) -> List[Issue]:
    out: List[Issue] = []
    meta = model.get("metadata") or {}
    if not meta.get("source_path"):
        out.append(Issue.new(category="metadata", severity="MEDIUM",
                             description="source_path missing from canonical model",
                             recommended_action="run extractor on an input file"))
    if not meta.get("source_hash"):
        out.append(Issue.new(category="integrity", severity="LOW",
                             description="source_hash missing from canonical model",
                             recommended_action="rebuild canonical after extraction"))
    return out


def _probe_structure(model: Dict[str, Any]) -> List[Issue]:
    out: List[Issue] = []
    chapters = model.get("chapters") or []
    if chapters:
        for c in chapters:
            if not (c.get("title") or "").strip():
                out.append(Issue.new(
                    category="structure", severity="HIGH",
                    description="empty chapter title",
                    location={"chapter_id": c.get("id")},
                    recommended_action="rename chapter"))
    headings = model.get("headings") if isinstance(model.get("headings"), list) else []
    prev = 0
    for h in headings:
        level = int(h.get("level", 1))
        if prev and level > prev + 1:
            out.append(Issue.new(
                category="structure", severity="MEDIUM",
                description=f"heading level jump {prev}→{level}",
                location={"heading_id": h.get("id")},
                recommended_action="promote heading or add intermediate level"))
        prev = level
    return out


def _probe_language(model: Dict[str, Any]) -> List[Issue]:
    out: List[Issue] = []
    lang = model.get("language")
    if not lang:
        out.append(Issue.new(
            category="language", severity="LOW",
            description="document language not set",
            recommended_action="set canonical.language to fr/en/…"))
    return out


def _probe_accessibility(model: Dict[str, Any]) -> List[Issue]:
    out: List[Issue] = []
    figures = model.get("figures") or []
    for f in figures:
        if isinstance(f, dict) and not f.get("alt_text"):
            out.append(Issue.new(
                category="accessibility", severity="LOW",
                description="figure missing alt_text",
                location={"figure_id": f.get("id")},
                recommended_action="add descriptive alt_text"))
    return out


# ── content probes ───────────────────────────────────────────

def _paragraphs(model: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [p for p in (model.get("paragraphs") or [])
            if (p.get("content") or "").strip()]


def _probe_double_spaces(model: Dict[str, Any]) -> List[Issue]:
    hits = [p["id"] for p in _paragraphs(model) if "  " in p["content"]]
    if not hits:
        return []
    return [Issue.new(
        category="typography", severity="MEDIUM",
        description=f"double spaces in {len(hits)} paragraph(s)",
        location={"paragraph_ids": hits[:10], "total": len(hits)},
        recommended_action="replace double spaces with single spaces")]


def _probe_french_nbsp(model: Dict[str, Any]) -> List[Issue]:
    if (model.get("language") or "fr") not in ("fr", "fr_FR"):
        return []
    pat = re.compile(r" [?!:;]|[0-9] ?%|[0-9] ?€")
    hits = [p["id"] for p in _paragraphs(model) if pat.search(p["content"])]
    if not hits:
        return []
    return [Issue.new(
        category="typography", severity="MEDIUM",
        description=f"missing non-breaking spaces before punctuation in {len(hits)} paragraph(s)",
        location={"paragraph_ids": hits[:10], "total": len(hits)},
        recommended_action="insert nbsp before ? ! : ; and after numbers before % €")]


def _probe_straight_quotes(model: Dict[str, Any]) -> List[Issue]:
    hits = [p["id"] for p in _paragraphs(model)
            if '"' in p["content"] or "'" in p["content"]]
    if not hits:
        return []
    sev = "MEDIUM" if (model.get("language") or "").startswith("fr") else "LOW"
    return [Issue.new(
        category="typography", severity=sev,
        description=f"straight quotes in {len(hits)} paragraph(s)",
        location={"paragraph_ids": hits[:10], "total": len(hits)},
        recommended_action="replace straight quotes with typographic quotes (« » or guillemets)")]


def _probe_lowercase_start(model: Dict[str, Any]) -> List[Issue]:
    hits = [p["id"] for p in _paragraphs(model)
            if len(p["content"]) > 30 and p["content"][0].islower()]
    if not hits:
        return []
    return [Issue.new(
        category="typography", severity="LOW",
        description=f"{len(hits)} paragraph(s) start with a lowercase letter",
        location={"paragraph_ids": hits[:10], "total": len(hits)},
        recommended_action="capitalize first letter of paragraphs")]


def _probe_empty_paragraphs(model: Dict[str, Any]) -> List[Issue]:
    all_paras = model.get("paragraphs") or []
    empty = [p["id"] for p in all_paras if not (p.get("content") or "").strip()]
    if len(empty) <= 5:
        return []
    return [Issue.new(
        category="structure", severity="LOW",
        description=f"{len(empty)} empty paragraph(s) detected (possible extra blank lines)",
        location={"total": len(empty)},
        recommended_action="remove excessive blank paragraphs")]


def _probe_trailing_spaces(model: Dict[str, Any]) -> List[Issue]:
    hits = [p["id"] for p in _paragraphs(model)
            if p["content"] != p["content"].rstrip()]
    if not hits:
        return []
    return [Issue.new(
        category="typography", severity="LOW",
        description=f"trailing whitespace in {len(hits)} paragraph(s)",
        location={"paragraph_ids": hits[:10], "total": len(hits)},
        recommended_action="strip trailing whitespace")]


for _p in (_probe_metadata, _probe_structure, _probe_language,
           _probe_accessibility,
           _probe_double_spaces, _probe_french_nbsp,
           _probe_straight_quotes, _probe_lowercase_start,
           _probe_empty_paragraphs, _probe_trailing_spaces):
    register_probe(_p)


# ── entry point ───────────────────────────────────────────────

def run_audit(model: Dict[str, Any], persist: bool = False) -> List[Issue]:
    issues: List[Issue] = []
    for probe in _PROBES:
        try:
            issues.extend(probe(model) or [])
        except Exception as e:  # noqa: BLE001
            emit("AUDIT_PROBE_ERROR", probe=probe.__name__, err=str(e))
    emit("AUDIT_DONE", issues=len(issues))
    if persist:
        save_all(issues)
    return issues
