# PLAN.md — Migration architecturale DocForge

## Objectif

Faire évoluer DocForge d'un moteur DOCX-first vers un **moteur universel
de traitement documentaire autonome** doté d'un contrat vérifiable, d'un
audit engine, d'une checklist priorisée, d'un completion engine avec
gates + evidence + score + best-version + regression check + boucle
d'amélioration autonome, tout en restant provider-agnostic et
retro-compatible avec la pipeline DOCX existante.

**Principe fondamental** : `NO CLAIM OF COMPLETION WITHOUT EVIDENCE.`

## Architecture cible (couches)

| Couche | Modules |
|--------|---------|
| A. Control Plane          | `docforge/orchestrator.py`, `controller.py`, `manager.py`, `scheduler.py`, `planner.py` |
| B. Universal Doc Kernel   | `docforge/formats/base.py`, `formats/docx/*`, `formats/txt/*`, `formats/markdown/*`, stubs pour xlsx/pdf/pptx/html/odt/csv |
| C. Canonical Doc Model    | `docforge/canonical.py` (étendu) |
| D. Audit Engine           | `docforge/audit/engine.py` |
| E. Issue/Checklist Engine | `docforge/audit/issues.py`, `audit/checklist.py` |
| F. Correction Engine      | `docforge/workers/builders.py` (existant, câblé via checklist) |
| G. Verification Engine    | `docforge/workers/verifiers.py` (existant) |
| H. Completion Engine      | `docforge/completion/{gates,evidence,completion_guard,contract}.py` |
| I. Score/Improvement Eng. | `docforge/completion/{score,regression,versioning}.py`, `docforge/improvement/loop.py` |
| J. Memory & State         | `docforge/state.py`, `memory.py`, `events.py` (déjà en place) |
| K. Provider/Runtime Adap. | `docforge/providers/*` (déjà en place) |
| L. CLI / Chat / Cowork    | `docforge/cli.py` (étendu), `bin/docforge`, `.docforge/chat/entrypoint.md` |

## Étapes (ordre d'exécution)

1. **PHASE A/B — Livrables planning** (ce fichier + `CONTRACT.yaml` +
   `DEFINITION_OF_DONE.yaml` + `GATES.md`).
2. **PHASE C — Universal Document Kernel**
   - `docforge/formats/base.py` : classe `UniversalDocumentAdapter` avec
     `parse/inspect/extract/normalize/render/modify/export/validate` et
     `capabilities: dict[str, bool]`.
   - Registry `docforge/formats/__init__.py`.
   - Adapter DOCX qui délègue aux scripts existants.
   - Adapters TXT et Markdown (lecture/écriture texte + audit basique).
   - Stubs XLSX, PDF, PPTX, HTML, ODT, CSV (déclarés indisponibles,
     `NotImplementedError` clair sur les opérations).
3. **PHASE D — Canonical Model étendu**
   - Étendre `docforge/canonical.py` : ajouter champs
     `slides/sheets/pages/blocks/tables/figures/images/charts/formulas/
     headers/footers/styles/references/citations/bibliography/hyperlinks/
     embedded_objects/external_dependencies/calculations/accessibility/
     provenance/issue_links/corrections/verification_evidence`.
   - IDs stables pour chaque élément (P######, TAB###, FIG###, EQ###).
4. **PHASE E — Audit Engine + Issue Registry + Checklist**
   - `docforge/audit/issues.py` : dataclass `Issue`, persistance
     `.docforge/audits/issues.jsonl`.
   - `docforge/audit/engine.py` : produit une liste d'Issues à partir
     du modèle canonique et de vérifications déterministes (réutilise
     `scripts/craft_audit.py` + `check_unicode.py` + `validate_layout.py`
     + `compare_docx.py`).
   - `docforge/audit/checklist.py` : transforme issues en tâches
     priorisées `.docforge/checklists/current.json`.
5. **PHASE F — Completion Engine**
   - `docforge/completion/contract.py` : chargement `CONTRACT.yaml`,
     couverture des exigences.
   - `docforge/completion/gates.py` : chargement `GATES.yaml`,
     évaluation d'une gate.
   - `docforge/completion/evidence.py` : append à
     `.docforge/completion/evidence.jsonl`, index par gate/tâche.
   - `docforge/completion/completion_guard.py` : refuse `DONE` tant
     qu'une gate obligatoire est ouverte ou sans preuve.
6. **PHASE G — Score / Regression / Versioning**
   - `docforge/completion/score.py` : dimensions sur 100, réutilise
     `craft_score.py`.
   - `docforge/completion/regression.py` : détection régression
     bloquante.
   - `docforge/completion/versioning.py` : baseline/current/previous/
     best/last_known_good sous `.docforge/scores/versions.json` + copies
     `.docforge/scores/best/`.
7. **PHASE H — Boucle d'amélioration autonome**
   - `docforge/improvement/loop.py` : `audit → correction → verify →
     score → compare → improve → repeat`, avec détection stagnation /
     oscillation / régression / budget.
8. **PHASE I — CLI et interfaces**
   - `docforge/cli.py` : ajouter `interview`, `audit`, `plan`, `verify`,
     `score`, `improve`, `final-audit`, `inspect`, `structure`,
     `language`, `format`, `layout`, `visual`, `tables`, `figures`,
     `formulas`, `references`.
   - `run.sh` : rester rétrocompatible.
9. **PHASE J — Tests**
   - `tests/test_formats.py`, `tests/test_audit_engine.py`,
     `tests/test_completion_gates.py`, `tests/test_evidence.py`,
     `tests/test_score.py`, `tests/test_regression.py`,
     `tests/test_versioning.py`, `tests/test_improvement_loop.py`,
     `tests/test_cli_new_commands.py`.
   - Tests d'échec volontaire : preuve manquante, exigence non couverte,
     régression, sortie invalide, agent qui prétend DONE sans evidence.
10. **PHASE K — Documentation**
    - Mise à jour `README.md`, `DOCFORGE.md`, `AGENTS.md`, `LOOP.yaml`,
      `CLAUDE.md`.
11. **PHASE L — Final audit**
    - Écrire `.docforge/project/IMPLEMENTATION_AUDIT.md` honnête
      (réalisé / partiel / non réalisé / dette).

## Stratégie de non-régression

- Le pipeline `Orchestrator.run()` actuel reste inchangé par défaut.
- Les nouveaux modules sont **opt-in** : le CompletionGuard n'est
  invoqué que si `.docforge/completion/GATES.yaml` existe.
- Le UniversalDocumentAdapter DOCX **délègue** aux `scripts/*` existants,
  aucun rewrite.
- Les 29 tests existants doivent rester verts après chaque phase.

## Critères de réussite

Chaque item du CONTRACT.yaml a un test unitaire ou une gate exécutable
qui prouve son fonctionnement. Voir `DEFINITION_OF_DONE.yaml` pour la
liste vérifiable et `GATES.md` pour les preuves.

## Ce qui n'est PAS fait dans cette migration

- Les adapters non-DOCX (XLSX, PDF, PPTX, HTML, ODT, CSV) sont livrés
  comme **stubs déclaratifs** qui refusent leurs opérations avec
  `NotImplementedError`. L'objectif est de garantir l'architecture,
  pas de mentir sur la capacité.
- Le rapport final couvre les nouvelles rubriques mais les rubriques
  visuelles (rendu comparatif de versions) restent minimales.
- L'Interview Engine est un stub interactif basique qui écrit un
  CONTRACT.yaml squelette. Un vrai dialogue conversationnel dépasse
  la portée d'une session.
