# DocForge — Agents

Chaque agent porte une responsabilité unique. Le core résout un nom en
callable Python (workers déterministes). Un provider externe peut
également porter le même rôle.

## Planification & gouvernance

- **planner** — construit et révise le graphe de tâches.
- **manager** — dispatch, files, priorités, dépendances, retries.
- **controller** — détecte stagnation/régression, ordonne REPLAN.
- **report-agent** — génère le rapport final (fr).

## Analyse

- **extractor** — extrait paragraphes/structure du document source (`inspect_docx.py`).
- **document-analyst** — synthèse de haut niveau.
- **structure-architect** — propose une structure reconstruite (`extract_structure.py`).
- **metadata-agent** — titre, auteur, langue, année, type.
- **coherence-agent** — cohérence titre / résumé / chapitres / dates.

## Rédaction

- **language-editor** — orthographe, grammaire, syntaxe, ponctuation, typographie fr.
- **style-editor** — clarté, lourdeurs, transitions, registre.
- **terminology-agent** — cohérence terminologique.

## Éléments documentaires

- **figure-agent**, **table-agent**, **reference-agent**, **citation-agent**, **equation-agent**.

## Mise en forme

- **formatting-agent** — police, taille, interligne, marges (`apply_styles.py`).
- **layout-agent** — retraits, sauts, veuves/orphelines.
- **pagination-agent**, **header-footer-agent**.

## Reconstruction

- **structure-applier** — applique la structure verrouillée (`apply_structure.py`).
- **manifest-builder** — construit le manifeste des chapitres (`create_manifest.py`).
- **document-builder** — fusionne les chapitres (`merge_docx.py`).
- **assembler** — assemble et met à jour les champs (`update_fields.py`).
- **exporter** — DOCX + PDF final (`export_pdf.py`).

## Contrôle

- **content-verifier** / **integrity-verifier** — `compare_docx.py`, changements non autorisés.
- **language-verifier** — `check_unicode.py`.
- **structure-verifier** — structure du modèle canonique.
- **format-verifier** / **layout-verifier** — `validate_layout.py`.
- **reference-verifier** — références croisées.
- **pdf-verifier** — audit visuel du PDF exporté.

## Ajout d'un agent

Créez `.docforge/agents/<name>.md` (description) et enregistrez le worker
dans `docforge/workers/` via `register(name, fn)`.
