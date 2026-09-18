# CLAUDE.md — DocForge (Claude Code adapter)

Ce fichier oriente Claude Code lorsqu'il est utilisé comme runtime pour
DocForge. La logique métier vit dans `docforge/` (Python) — ce fichier
ne décrit que l'adaptation Claude Code.

## Identité du projet

- Nom : **DocForge** (anciennement « Loop »).
- Commande principale : `docforge` (via `bin/docforge`).
- Rôle : moteur autonome multi-agents de reconstruction, correction,
  mise en forme et contrôle qualité documentaire.

## Règles système (toujours applicables)

1. Ne jamais réécrire un long document entièrement.
2. Utiliser un état persistant (`.docforge/state/`).
3. Journaliser (`.docforge/memory/events.jsonl`).
4. Utiliser des IDs stables (P000001…) + SHA-256.
5. Séparer builders et verifiers.
6. Le workflow ne pause plus pour attendre une validation humaine :
   il s'exécute jusqu'à DONE, DONE_WITH_REVIEW_ITEMS, BLOCKED ou
   FAILED_SYSTEM. Les décisions incertaines sont écrites dans
   `.docforge/state/manual_review.json`.
7. Ne jamais modifier un contenu sans traçabilité.
8. Après 5 échecs locaux → `PENDING_MANUAL`, on passe au suivant.
9. Un échec local ne bloque pas la boucle.
10. La sortie doit être reproductible depuis le state.
11. Rapport final toujours produit (`output/DOCFORGE_REPORT.md`).
12. La sortie IA n'est jamais une preuve : les verifiers déterministes
    ont le dernier mot.

## Architecture

```
.docforge/         état persistant, config, modèle canonique, mémoire, chat
docforge/          cœur Python agnostique (Planner/Manager/Controller/…)
docforge/providers/ adapters (claude-code, codex, gemini, cursor, qwen, opencode, generic)
docforge/workers/   builders + verifiers déterministes
adapters/          adaptateurs plateforme (mince)
scripts/           scripts déterministes DOCX/PDF (réutilisés)
.claude/           agents + skills Claude Code (adaptateur legacy)
input/ work/ output/ logs/
bin/docforge       exécutable
run.sh             wrapper LEGACY vers docforge
DOCFORGE.md AGENTS.md LOOP.yaml  protocole portable (mode chat)
```

## Boucle DocForge

```
PLAN → BUILD → VERIFY → MEMORY → CONTROL → REPLAN
```

Autonome. Aucune pause humaine.

## Commandes

```bash
docforge init | doctor | providers | workers | run | status | audit
docforge report | resume | pause | stop | reset --force
```

Le wrapper legacy `./run.sh` reste disponible pendant la migration.

## Adaptation Claude Code

- Les fichiers `.claude/agents/*.md` restent en place comme documentation
  agent lisible par Claude Code.
- Les fichiers `.claude/skills/*` restent en place.
- La logique n'est plus dans `.claude/` : elle est dans `docforge/`.

## Ajouter un agent

1. `.docforge/agents/<name>.md` (description + rôle).
2. Enregistrer un worker Python dans `docforge/workers/` via `register`.
3. Optionnel : `.claude/agents/<name>.md` si l'agent doit être invocable
   depuis Claude Code interactif.

## Ajouter un skill

1. `.docforge/skills/<name>/SKILL.md` avec triggers + règles.
2. Réutiliser via `docforge/workers/` si besoin.

## Document Craft System

After GLOBAL_QA passes and before EXPORT, the loop enters the **DOCUMENT_CRAFT** pipeline.
This system gives DocForge editorial taste, typographic craft, and visual quality.

### Craft Pipeline

```
GLOBAL_QA (pass)
    → DOCUMENT_CRAFT
        → CRAFT_TASTE         (design direction)
        → CRAFT_TYPOGRAPHY    (typographic optimization)
        → CRAFT_HIERARCHY     (visual hierarchy verification)
        → CRAFT_RHYTHM        (document rhythm analysis)
        → CRAFT_COMPOSITION   (page composition analysis)
        → CRAFT_HUMAN_FINISH  (anti-mechanical-generation)
        → CRAFT_AUDIT         (full quality audit)
        → CRAFT_POLISH        (final finishing)
    → EXPORT
```

### Craft Architecture

```
ART DIRECTOR (design_direction.yaml)
       ↓
BUILDERS (parallel where independent)
  ├── TYPOGRAPHIC EDITOR
  ├── PAGE COMPOSER
  ├── EDITORIAL CRAFT EDITOR
  ├── HUMAN FINISH EDITOR
  └── DOCUMENT RHYTHM
       ↓
DOCUMENT AUDITOR (read-only verifier)
       ↓
DOCUMENT POLISHER
       ↓
CONTROLLER
```

### Craft Commands

```bash
./run.sh craft          # Full editorial quality pipeline
./run.sh taste          # Editorial taste → design direction
./run.sh typography     # Typographic optimization
./run.sh composition    # Page composition analysis
./run.sh rhythm         # Document rhythm analysis
./run.sh polish         # Final polish pass
./run.sh humanize       # Reduce mechanical generation signs
./run.sh audit          # Document craft audit
./run.sh visual-audit   # PDF visual audit
```

### Design Direction

The Art Director produces `.docforge/model/design_direction.yaml`, which all
craft agents read. It defines: document_type, visual_style, density, typography
approach, spacing philosophy, hierarchy method, table/figure treatment, and
finish level.

### Quality Dimensions

Internal quality scoring across 10 dimensions (0-4 each):
typography, hierarchy, spacing, composition, density, consistency,
tables, figures, pagination, human_finish

### Separation Principle

- **Builders** modify the document (typographic-editor, page-composer, etc.)
- **Auditor** evaluates the document (document-auditor — has NO Write tool)
- **Polisher** applies final fixes (document-polisher)
- An agent that corrects is NEVER its own verifier
