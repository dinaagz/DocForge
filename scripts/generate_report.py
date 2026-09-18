#!/usr/bin/env python3
"""
generate_report.py — Generate the final quality report.

Collects data from all state files and produces:
  output/rapport_qualite.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from common import (
    OUTPUT_DIR, WORK_DIR, get_logger, load_config, load_state, log_event, now_iso,
)

logger = get_logger("report")


def generate() -> str:
    cfg = load_config()
    manifest = load_state("document_manifest")
    locked = load_state("structure_locked")
    ch_status = load_state("chapter_status")
    corrections = load_state("corrections")
    quality_log = load_state("quality_log")
    loop_state = load_state("loop_state")
    validation = load_state("validation_issues")

    doc_name = cfg.get("document", {}).get("name", "Unknown")

    lines: List[str] = []
    lines.append("# Rapport Qualité — Traitement de Document")
    lines.append("")
    lines.append(f"**Document :** {doc_name}")
    lines.append(f"**Date :** {now_iso()}")
    lines.append(f"**Statut workflow :** {loop_state.get('status', 'UNKNOWN')}")
    lines.append("")

    # 1. Summary
    lines.append("## 1. Résumé du document")
    lines.append("")
    if manifest:
        stats = manifest.get("statistics", {})
        lines.append(f"- Paragraphes : {stats.get('paragraph_count', '?')}")
        lines.append(f"- Pages estimées : {stats.get('estimated_pages', '?')}")
        lines.append(f"- Tableaux : {stats.get('table_count', '?')}")
        lines.append(f"- Images : {stats.get('image_count', '?')}")
        lines.append(f"- Notes de bas de page : {stats.get('footnote_count', '?')}")
    lines.append("")

    # 2. Final structure
    lines.append("## 2. Structure finale validée")
    lines.append("")
    if locked:
        for sec in locked.get("sections", []):
            indent = "  " * (sec.get("level", 1) - 1)
            lines.append(f"{indent}- **{sec.get('title', '?')}** (niveau {sec.get('level', '?')})")
    else:
        lines.append("*Structure non encore validée.*")
    lines.append("")

    # 3. Chapter status
    lines.append("## 3. Statut des chapitres")
    lines.append("")
    if ch_status and ch_status.get("chapters"):
        lines.append("| Chapitre | Titre | Statut | Itérations |")
        lines.append("|----------|-------|--------|------------|")
        for ch in ch_status["chapters"]:
            lines.append(f"| {ch['id']} | {ch.get('title', '?')[:40]} | {ch['status']} | {ch['iterations']} |")
    lines.append("")

    # 4. Corrections
    lines.append("## 4. Corrections linguistiques")
    lines.append("")
    if corrections:
        total = corrections.get("total_applied", 0)
        lines.append(f"- Total corrections appliquées : {total}")
        by_cat: Dict[str, int] = {}
        for c in corrections.get("corrections", []):
            cat = c.get("category", "other")
            by_cat[cat] = by_cat.get(cat, 0) + 1
        for cat, cnt in sorted(by_cat.items()):
            lines.append(f"  - {cat} : {cnt}")
    else:
        lines.append("*Aucune correction enregistrée.*")
    lines.append("")

    # 5. Validation issues
    lines.append("## 5. Anomalies détectées")
    lines.append("")
    if validation:
        by_cls = validation.get("by_classification", {})
        for cls, cnt in sorted(by_cls.items()):
            lines.append(f"- {cls} : {cnt}")
        manual = [d for d in validation.get("diffs", []) if d.get("classification") == "MANUAL_REVIEW"]
        if manual:
            lines.append("")
            lines.append(f"### Éléments nécessitant validation humaine ({len(manual)})")
            for d in manual[:20]:
                lines.append(f"- {d.get('id', '?')} — {d.get('type', '?')}")
    lines.append("")

    # 6. Quality log
    lines.append("## 6. Résultats contrôle qualité")
    lines.append("")
    if quality_log and quality_log.get("checks"):
        for check in quality_log["checks"][-10:]:
            lines.append(f"- **{check.get('criterion', '?')}** : {check.get('result', '?')} ({check.get('chapter', 'global')})")
    lines.append("")

    # 7. Problèmes persistants
    lines.append("## 7. Problèmes persistants")
    lines.append("")
    pending = []
    if ch_status:
        pending = [ch for ch in ch_status.get("chapters", []) if ch["status"] == "PENDING_MANUAL"]
    if pending:
        for ch in pending:
            lines.append(f"- {ch['id']} ({ch.get('title', '?')}) — PENDING_MANUAL après {ch['iterations']} itérations")
            for iss in ch.get("issues", []):
                lines.append(f"  - {iss}")
    else:
        lines.append("*Aucun problème persistant.*")
    lines.append("")

    # 8. Generated files
    lines.append("## 8. Fichiers générés")
    lines.append("")
    for d in [OUTPUT_DIR, WORK_DIR / "assembled"]:
        if d.exists():
            for f in sorted(d.iterdir()):
                if f.is_file():
                    lines.append(f"- `{f.relative_to(f.parent.parent.parent) if len(f.parts) > 3 else f.name}`")
    lines.append("")

    # 9. Document Craft results
    lines.append("## 9. Document Craft — Qualité éditoriale")
    lines.append("")
    craft_audit = load_state("craft_audit")
    if craft_audit:
        lines.append(f"- Issues totales : {craft_audit.get('total_issues', 0)}")
        lines.append(f"- Critiques : {craft_audit.get('critical', 0)}")
        lines.append(f"- Haute sévérité : {craft_audit.get('high', 0)}")
        lines.append("")
        by_cat: Dict[str, int] = {}
        for iss in craft_audit.get("issues", [])[:30]:
            cat = iss.get("category", "OTHER")
            by_cat[cat] = by_cat.get(cat, 0) + 1
        if by_cat:
            lines.append("| Catégorie | Nombre |")
            lines.append("|-----------|--------|")
            for cat, cnt in sorted(by_cat.items()):
                lines.append(f"| {cat} | {cnt} |")
    else:
        lines.append("*Aucun audit Document Craft effectué.*")
    lines.append("")

    lines.append("---")
    lines.append("*Rapport généré automatiquement par le loop agentique.*")

    return "\n".join(lines)


def main() -> int:
    report = generate()
    out = OUTPUT_DIR / "rapport_qualite.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")

    log_event("REPORT_GENERATED", output=str(out))
    logger.info("Report written to %s", out)
    print(json.dumps({"status": "ok", "output": str(out)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
