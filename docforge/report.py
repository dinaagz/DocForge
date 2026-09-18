"""Final report — always in French."""
from __future__ import annotations

import json
from typing import Tuple

from .canonical import load_canonical
from .events import now_iso
from .memory import read as memread
from .paths import OUTPUT_DIR, ensure_layout
from .state import store
from .tasks import TaskQueue


def build_report() -> Tuple[str, str]:
    ensure_layout()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    q = TaskQueue()
    counts = q.counts()
    doc = load_canonical()
    sys_state = store.load("system", {})
    manual = store.load("manual_review", {"items": []})

    corrections = memread("corrections")
    decisions = memread("decisions")

    md_path = OUTPUT_DIR / "DOCFORGE_REPORT.md"
    json_path = OUTPUT_DIR / "DOCFORGE_REPORT.json"

    md = []
    md.append("# Rapport DocForge\n")
    md.append(f"_Généré le {now_iso()}_\n")
    md.append("## Résumé\n")
    md.append(f"- Statut final : **{sys_state.get('status', 'INCONNU')}**")
    md.append(f"- Itérations globales : {sys_state.get('iteration', 0)}")
    md.append(f"- Tâches totales : {sum(counts.values())}")
    md.append(f"- Tâches complétées : {counts.get('COMPLETED', 0)}")
    md.append(f"- Tâches échouées : {counts.get('FAILED', 0)}")
    md.append(f"- En revue manuelle : {counts.get('PENDING_MANUAL', 0) + len(manual.get('items', []))}\n")

    md.append("## Document canonique\n")
    if doc:
        meta = doc.get("metadata", {})
        md.append(f"- Source : `{meta.get('source_path', '—')}`")
        md.append(f"- Empreinte source : `{meta.get('source_hash', '—')}`")
        md.append(f"- Langue : {doc.get('language', '—')}")
        md.append(f"- Profil de style : {doc.get('style_profile', '—')}")
        md.append(f"- Chapitres : {len(doc.get('chapters', []))}")
        md.append(f"- Paragraphes : {len(doc.get('paragraphs', []))}\n")
        md.append("### Structure reconstruite\n")
        for c in doc.get("chapters", []):
            md.append(f"- **{c['id']}** — {c['title']}")
        md.append("")
    else:
        md.append("_Aucun modèle canonique disponible._\n")

    md.append("## Agents exécutés\n")
    agents = {}
    for t in q.tasks.values():
        agents[t.agent] = agents.get(t.agent, 0) + 1
    for a, n in sorted(agents.items(), key=lambda x: -x[1]):
        md.append(f"- `{a}` — {n} tâche(s)")
    md.append("")

    md.append("## Corrections appliquées\n")
    if corrections:
        for c in corrections[-25:]:
            md.append(f"- `{c.get('agent', '?')}` sur `{c.get('target', '?')}` : {c.get('rationale', '')}")
    else:
        md.append("_Aucune correction enregistrée._")
    md.append("")

    md.append("## Décisions du planificateur\n")
    for d in decisions[-10:]:
        md.append(f"- **{d.get('topic', '?')}** → {d.get('choice', '?')} ({d.get('rationale', '')})")
    md.append("")

    if manual.get("items"):
        md.append("## Éléments laissés en revue manuelle\n")
        for it in manual["items"]:
            md.append(f"- `{it.get('id')}` [{it.get('confidence')}] : {it.get('reason')}")
        md.append("")

    md.append("## Statut final\n")
    md.append(f"`{sys_state.get('status', 'INCONNU')}`\n")

    md_path.write_text("\n".join(md), encoding="utf-8")
    json_path.write_text(json.dumps({
        "generated_at": now_iso(),
        "status": sys_state.get("status"),
        "iterations": sys_state.get("iteration"),
        "counts": counts,
        "agents": agents,
        "canonical": {
            "chapters": len(doc.get("chapters", [])) if doc else 0,
            "paragraphs": len(doc.get("paragraphs", [])) if doc else 0,
            "source_hash": doc.get("metadata", {}).get("source_hash", "") if doc else "",
        },
        "manual_review": manual.get("items", []),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    return str(md_path), str(json_path)
