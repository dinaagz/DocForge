# REPO_AUDIT.md — DocForge

_Audit effectué avant toute modification (Phase A du prompt maître de migration architecturale)._

## 1. État actuel du repository

### 1.1. Arborescence principale

```
docforge/            # cœur Python (Planner, Manager, Controller, Scheduler)
  cli.py             # CLI unique
  orchestrator.py    # boucle PLAN → BUILD → VERIFY → MEMORY → CONTROL → REPLAN
  planner.py         # graphe de tâches (pipeline DOCX fixe)
  manager.py         # dispatch tâches → provider
  controller.py      # stagnation/régression → REPLAN/BLOCKED
  scheduler.py       # ThreadPool + resource locks
  tasks.py           # TaskQueue persistante
  state.py           # store JSON atomique
  memory.py          # decisions/corrections/hypotheses (jsonl)
  events.py          # events.jsonl append-only
  canonical.py       # modèle canonique (DOCX-first, plat)
  paths.py           # layout FS
  config.py          # yaml + defaults + profils
  capabilities.py    # detection runtime
  report.py          # DOCFORGE_REPORT.{md,json}
  providers/         # 7 adapters (generic, claude-code, codex, gemini,
                     #             cursor, qwen, opencode)
  workers/           # builders.py, verifiers.py (wrappers scripts/)
scripts/             # 15+ scripts DOCX déterministes (loop.py legacy 1201 l.)
adapters/            # adapter.yaml plateforme (mince, docs)
.docforge/           # config, skills, profiles, providers, schemas, chat…
.claude/             # agents + skills legacy
config/              # document_config.yaml legacy
state/               # loop_state.example.json legacy
tests/               # 29 tests (tous verts après install python-docx + pyyaml)
input/ work/ output/ logs/
bin/docforge run.sh docforge_cli.py install.sh install.ps1
CLAUDE.md DOCFORGE.md AGENTS.md LOOP.yaml README.md .mcp.json
```

### 1.2. Comptes de lignes (Python métier)

- Cœur (`docforge/**/*.py`) : ~1 200 lignes
- Scripts déterministes (`scripts/*.py`) : ~4 100 lignes (dont `loop.py` legacy 1 201 l.)
- Tests : ~470 lignes, 29 tests, tous verts (nécessite `python-docx` et `pyyaml`).

### 1.3. Boucle exécutable réelle

`Orchestrator.run()` (docforge/orchestrator.py:35) exécute jusqu'à un état
terminal (`DONE`, `DONE_WITH_REVIEW_ITEMS`, `BLOCKED`). Aucune pause humaine.

Plan initial produit 15 tâches figées DOCX-only :
extract → structure_extract → canonical_build → analyses parallèles
(language/coherence/structure_verify) → structure_apply → manifest → format
→ assemble → 4 verifiers → export → pdf_verify → final_report.

## 2. Architecture réelle (fonctionne)

- Provider-agnostic déjà partiellement en place (`ProviderAdapter` base,
  7 adapters, sélection par préférence, fallback sur `generic`).
- Séparation builders/verifiers en place (workers/builders.py vs
  workers/verifiers.py) — rule §5.
- État persistant atomique (state.py `os.replace`).
- Journal d'événements append-only (events.jsonl).
- Mémoire structurée (decisions/corrections/hypotheses jsonl).
- ResourceLocks basiques dans le scheduler.
- Manual-review queue simple (state/manual_review.json).
- Reprise possible via TaskQueue persistante.
- Rapport final `output/DOCFORGE_REPORT.{md,json}` toujours produit.
- ~29 tests unitaires verts couvrant : inspection DOCX, comparaison,
  structure, unicode, `state.py`, orchestrator smoke, planner.

## 3. Architecture documentée mais partiellement implémentée

Le README.md (17 k) et CLAUDE.md décrivent :
- Un **Document Craft System** (Art Director → 5 builders parallèles →
  Auditor → Polisher). Présent sous forme de :
  - `.docforge/model/design_direction.yaml` (skeleton)
  - `.docforge/skills/document-craft/*/SKILL.md` (docs uniquement)
  - `.claude/agents/*.md` (docs Claude Code uniquement)
  - `scripts/craft_score.py`, `scripts/craft_audit.py` (déterministes,
    scoring et audit qualité, mais NON câblés dans la boucle Python
    principale — la pipeline dans `planner.py` ne les invoque pas).
- Une DOCUMENT_CRAFT pipeline (CRAFT_TASTE → … → CRAFT_POLISH →
  CRAFT_AUDIT → EXPORT). Elle est **documentée mais non exécutée** par
  `Orchestrator`. Seuls `run.sh craft/taste/typography/…` (wrapper shell)
  peuvent l'invoquer manuellement.

## 4. Écart entre code et documentation (les faits)

| Décrit                                             | Code réel        |
|---------------------------------------------------|------------------|
| DOCUMENT_CRAFT pipeline autonome                   | Non intégré      |
| Universal Document Kernel multi-format             | DOCX-only        |
| Audit Engine indépendant                           | Verifiers seulement |
| Issue Registry / Checklist Engine                  | Absent           |
| Completion Engine (gates, evidence, guard)         | Absent           |
| Score Engine sur 100                               | `craft_score.py` isolé |
| Best-version + regression check                    | Absent           |
| Interview Engine / Contract / DoD                  | Absent           |
| Boucle d'amélioration autonome                     | Basique (stagnation/regression counts) |
| Commandes `/DocForge` universelles                 | Absent (CLI docforge seulement) |
| Séparation `contract`/`audit`/`completion` en Py   | Absent           |

## 5. Composants réutilisables

- **TOUT `docforge/`** (state, events, memory, tasks, scheduler,
  controller, planner squelette, providers, workers). Solide, testé.
- **TOUT `scripts/*.py`** — scripts DOCX déterministes battle-tested.
- **`craft_score.py`** — dimensions déjà proches du Score Engine cible.
- **`craft_audit.py`** — audit qualité déterministe réutilisable comme
  premier moteur d'audit.
- Schémas JSON existants (canonical, task).
- Providers registry — pattern à généraliser pour les formats.

## 6. Composants à modifier

- `docforge/canonical.py` : étendre le modèle canonique (slides, sheets,
  cells, pages, blocks, refs, provenance, evidence links).
- `docforge/planner.py` : remplacer la pipeline figée par des phases
  paramétrées par le format et le contrat.
- `docforge/controller.py` : intégrer le Completion Guard et la logique
  best-version au lieu de la seule stagnation/regression.
- `docforge/manager.py` : dispatcher aussi les tâches d'audit, checklist,
  gates, score, evidence.
- `docforge/report.py` : rapport final aligné sur DoD (rubriques
  contract/audit/checklist/scores/best-version/evidence/gates).
- `docforge/cli.py` : nouvelles sous-commandes (`interview`, `audit`,
  `plan`, `verify`, `score`, `improve`, `final-audit`, `inspect`,
  `structure`, `language`, `format`, `layout`, `visual`, `tables`,
  `figures`, `formulas`, `references`).

## 7. Composants à créer (nouveaux modules)

- `docforge/formats/` : `base.py` (UniversalDocumentAdapter), puis
  `docx/`, `xlsx/`, `pdf/`, `pptx/`, `html/`, `odt/`, `csv/`, `txt/`,
  `markdown/` (au moins DOCX fonctionnel, autres stubs déclaratifs).
- `docforge/audit/` : `engine.py`, `issues.py`, `checklist.py`.
- `docforge/completion/` : `contract.py`, `gates.py`, `evidence.py`,
  `completion_guard.py`, `regression.py`, `score.py`, `versioning.py`.
- `docforge/contract/` : `interviewer.py`.
- `docforge/improvement/` : `loop.py` (audit → correction → verify → score
  → compare → improve → repeat).
- `.docforge/completion/` : `GATES.yaml`, `EVIDENCE.jsonl`, `SCORECARD.yaml`.
- `.docforge/project/` : `REPO_AUDIT.md`, `PLAN.md`, `CONTRACT.yaml`,
  `DEFINITION_OF_DONE.yaml`, `IMPLEMENTATION_AUDIT.md`.
- Tests correspondants sous `tests/`.

## 8. Duplications / composants obsolètes

- `scripts/loop.py` (1 201 l.) — code legacy de la version « Loop ». La
  boucle Python `Orchestrator` fait désormais autorité. À conserver
  comme référence (le README y renvoie encore via `./run.sh`), mais ne
  pas s'appuyer dessus pour la nouvelle architecture.
- `state/loop_state.example.json` — legacy.
- `.claude/agents/*.md` et `.docforge/skills/document-craft/*` :
  documentation uniquement, à conserver mais ne portent aucune logique.
- Deux répertoires de skills (`.claude/skills` et `.docforge/skills`).
  Documentaires : à laisser en l'état.

## 9. Risques identifiés

1. **Casser la pipeline DOCX existante en généralisant.** Mitigation :
   introduire `UniversalDocumentAdapter` avec DOCX comme adapter par
   défaut réutilisant les scripts existants. Les 29 tests actuels
   servent de filet.
2. **Fantômer des capacités multi-format.** Le prompt interdit
   explicitement les capacités déclarées sans implémentation. Les
   adapters non-DOCX seront livrés comme **stubs déclaratifs** clairement
   marqués `capabilities: []` et `implemented: false`, refusant les
   opérations non implémentées avec `NotImplementedError` explicite —
   pas de faux positifs.
3. **Corruption de l'état.** Ne pas rompre le schéma persisté existant.
   Le CompletionEngine et l'IssueRegistry écrivent dans des fichiers
   **additifs** (jsonl / yaml séparés) et ne modifient pas le schéma
   `tasks.json`/`system.json`.
4. **Perte du filet de test.** Toute nouvelle capacité s'accompagne
   d'au moins un test unitaire. Aucune suppression de test existant.
5. **Dérive « théorique ».** Le CompletionGuard vérifie que chaque
   Gate a une commande exécutable ou une preuve concrète. Une gate qui
   ne peut pas échouer est refusée à l'entrée.

## 10. Dépendances

- Runtime : Python 3.11, `python-docx`, `PyYAML`, `pytest`.
- Système : `libreoffice`/`soffice` pour PDF (déjà géré par
  `capabilities.detect`).
- Providers : optionnels (CLI présentes sont détectées mais leur
  indisponibilité ne bloque pas — `generic` est fallback).

## 11. Plan de migration (résumé — détail dans PLAN.md)

Migration **additive** et **progressive** :

1. Écrire PLAN + CONTRACT + DoD + GATES.
2. Créer `docforge/formats/base.py` + adapter DOCX qui délègue à
   `scripts/*` existants. Le core continue de fonctionner sans changement.
3. Ajouter `docforge/audit/`, `docforge/completion/`,
   `docforge/contract/`, `docforge/improvement/` en tant que **modules
   autonomes** avec APIs pures Python et fichiers d'état séparés.
4. Ajouter des sous-commandes CLI `interview`, `audit`, `plan`, `verify`,
   `score`, `improve`, `final-audit`.
5. Câbler `Controller` : après la boucle actuelle, appeler le
   CompletionGuard sur les gates avant de retourner `DONE`.
6. Câbler `report.py` : ajouter les rubriques exigées par la DoD.
7. Ajouter les tests, faire tourner `pytest`.
8. Écrire IMPLEMENTATION_AUDIT.md, honnête sur ce qui est fait, partiel,
   ou différé.

## 12. Ce que cette migration ne fera PAS (honnête)

- Elle ne rendra pas XLSX/PDF/PPTX/HTML/ODT/CSV/MD **exécutables** en une
  seule session. Elle installe l'**architecture** pour les recevoir
  (`UniversalDocumentAdapter`, registry) et fournit **DOCX fonctionnel**
  et **TXT/Markdown minimalement fonctionnels** (lecture/écriture texte
  brut). Les autres formats seront enregistrés comme adapters stub qui
  refusent leurs opérations avec un message clair.
- Elle ne remplacera pas le fond de `craft_score.py` — elle le
  **réutilisera** comme moteur de scoring initial, wrappé par
  `docforge/completion/score.py`.
- Elle ne réécrira pas `scripts/loop.py` legacy.
- Elle ne modifiera pas les 29 tests existants.

_Le PLAN.md détaille l'ordre et la définition de DONE._
