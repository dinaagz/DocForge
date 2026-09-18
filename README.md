# Agentic Document Processing Loop

A framework for processing long academic documents (DOCX/PDF) using an agentic loop with persistent state, iterative quality control, and mandatory human validation.

## Features

- **Persistent state machine** — survives interruptions, resumes automatically
- **Chapter-by-chapter processing** — never processes the entire document at once
- **Separation of concerns** — specialized agents for inspection, analysis, language, formatting, verification, and quality control
- **Human-in-the-loop** — structure proposals require explicit validation
- **Iterative QA** — up to 5 quality iterations per chapter, then escalates
- **Document safety** — never modifies substantive content; all changes are logged and reversible
- **Deterministic tools** — Python scripts handle all DOCX modifications; Claude handles analysis and decisions

## Architecture

```
project-root/
├── .claude/
│   ├── CLAUDE.md                    # System rules
│   ├── agents/                      # Specialized sub-agents
│   │   ├── document-inspector.md
│   │   ├── structure-analyst.md
│   │   ├── language-reviewer.md
│   │   ├── formatting-specialist.md
│   │   ├── integrity-verifier.md
│   │   ├── quality-controller.md
│   │   ├── assembler.md
│   │   └── final-auditor.md
│   └── skills/                      # Business rules
│       ├── document-inspection/
│       ├── structure-analysis/
│       ├── language-quality/
│       ├── docx-formatting/
│       ├── integrity-validation/
│       ├── chapter-processing/
│       ├── quality-loop/
│       ├── document-assembly/
│       └── final-audit/
├── config/
│   └── document_config.yaml         # All processing parameters
├── scripts/                         # Deterministic Python tools
│   ├── loop.py                      # State machine engine
│   ├── inspect_docx.py
│   ├── extract_structure.py
│   ├── apply_structure.py
│   ├── apply_styles.py
│   ├── language_diff.py
│   ├── compare_docx.py
│   ├── check_unicode.py
│   ├── validate_layout.py
│   ├── update_fields.py
│   ├── merge_docx.py
│   ├── export_pdf.py
│   └── generate_report.py
├── state/                           # Persistent state (JSON)
├── logs/                            # Event journal + error logs
├── input/                           # Place source DOCX here
├── work/                            # Working files
├── output/                          # Final deliverables
├── run.sh                           # Heartbeat launcher
└── requirements.txt
```

## Installation

```bash
pip3 install -r requirements.txt
```

LibreOffice is required for PDF export:
```bash
# Ubuntu/Debian
sudo apt-get install libreoffice
```

## Quick Start

1. **Place your document** in `input/`:
   ```bash
   cp your_document.docx input/Memoire_Fin_d_année.docx
   ```

2. **Configure** (optional): edit `config/document_config.yaml` to match your document name and formatting preferences.

3. **Start the loop**:
   ```bash
   ./run.sh run
   ```

4. **Check status**:
   ```bash
   ./run.sh status
   ```

5. **When prompted for validation**: review `work/inspection/structure_proposal.md`, then:
   ```bash
   ./run.sh validate
   ```

6. **Continue processing**:
   ```bash
   ./run.sh run
   # or for continuous processing:
   ./run.sh loop
   ```

## Commands

| Command | Description |
|---------|-------------|
| `./run.sh status` | Show current workflow state |
| `./run.sh run` | Execute one step of the state machine |
| `./run.sh run --steps 5` | Execute up to 5 steps |
| `./run.sh resume` | Resume from last interrupted state |
| `./run.sh validate` | Validate the proposed structure |
| `./run.sh loop` | Continuous heartbeat until terminal state |
| `./run.sh reset --force` | Reset workflow to initial state |
| `./run.sh inspect` | Run document inspection only |
| `./run.sh analyze` | Run structure analysis only |
| `./run.sh assemble` | Assemble chapters only |
| `./run.sh export` | Export DOCX + PDF only |
| `./run.sh report` | Generate final quality report |

## State Machine

```
INIT → INSPECTION → STRUCTURE_ANALYSIS → WAITING_FOR_HUMAN_VALIDATION
    → STRUCTURE_LOCKED → CHAPTER_PROCESSING → CHAPTER_QA
    → (iterate up to 5x) → CHAPTER_VALIDATED → NEXT_CHAPTER
    → ASSEMBLY → GLOBAL_QA → EXPORT → FINAL_REPORT → DONE
```

### Failure handling

- Chapter QA fails after 5 iterations → `PENDING_MANUAL` → continues with next chapter
- Global QA fails after 5 iterations → `BLOCKED` → requires manual intervention
- Any error → logged, state preserved, resumable

## Resuming After Interruption

The loop is fully restart-safe. State is saved in `state/loop_state.json` after every step.

```bash
# Process was interrupted after chapter 4?
# It will resume at chapter 5:
./run.sh resume
```

## Persistent State Files

| File | Purpose |
|------|---------|
| `state/loop_state.json` | Current phase, chapter, iteration |
| `state/document_manifest.json` | Full paragraph inventory with IDs |
| `state/structure_proposal.json` | Proposed heading hierarchy |
| `state/structure_locked.json` | Validated (locked) structure |
| `state/chapter_status.json` | Per-chapter processing status |
| `state/corrections.json` | All language corrections applied |
| `state/quality_log.json` | QA check results |
| `state/validation_issues.json` | Integrity comparison results |

## Adding a New Skill

1. Create `.claude/skills/<skill-name>/SKILL.md`
2. Define: trigger conditions, process steps, rules, output format
3. The skill will be available to agents automatically

## Adding a New Agent

1. Create `.claude/agents/<agent-name>.md`
2. Add frontmatter: name, description, model, tools
3. Write instructions following the existing agent patterns

## Adding a Connector

1. Edit `.mcp.json` to add the MCP server configuration
2. Mark as `OPTIONAL` if not required for core functionality
3. The framework works without external connectors

## Troubleshooting

- **"Lock already held"**: Another loop instance is running, or a previous run crashed. Wait 30 minutes for automatic lock release, or delete `state/.loop.lock`.
- **"File not found"**: Ensure your DOCX is in `input/` and the filename matches `config/document_config.yaml`.
- **Stuck in WAITING_FOR_HUMAN_VALIDATION**: Review the proposal and run `./run.sh validate`.
- **Chapter PENDING_MANUAL**: Review `work/qa/<chapter_id>_report.json` for details.
- **BLOCKED**: Review `state/quality_log.json` and `output/rapport_qualite.md` for global QA failures.

## Document Craft

DocForge inclut un système complet de qualité éditoriale et visuelle. Après la
reconstruction et le contrôle qualité technique, le pipeline Document Craft
transforme un document techniquement correct en un document qui paraît
professionnel, naturel et intentionnellement composé.

### Compétences (Skills)

| Compétence | Description |
|-----------|-------------|
| `editorial-taste` | Goût éditorial — hiérarchie, équilibre, densité, contraste, retenue |
| `typographic-craft` | Typographie — polices, tailles, poids, interligne, échelle, espacement |
| `document-rhythm` | Rythme — variation des paragraphes, alternance texte/table/figure, densité |
| `visual-hierarchy` | Hiérarchie visuelle — dominance, poids, position, ordre de lecture |
| `page-composition` | Composition — alignement, respiration, équilibre, blancs, figures, tableaux |
| `human-finish` | Finition humaine — détection de mise en page mécanique ou générique |
| `anti-slop-document` | Anti-slop — détection de surdesign, décorations inutiles, motifs artificiels |
| `editorial-consistency` | Cohérence — uniformité des styles à travers le document |
| `document-audit` | Audit — contrôle systématique par page, chapitre et document |
| `document-polish` | Polish — dernière passe de finition, corrections mineures restantes |

### Agents

| Agent | Rôle | Vérificateur |
|-------|------|-------------|
| `document-art-director` | Direction éditoriale et visuelle globale | — |
| `typographic-editor` | Optimisation typographique | document-auditor |
| `page-composer` | Composition des pages | document-auditor |
| `editorial-craft-editor` | Qualité éditoriale et rythme | document-auditor |
| `human-finish-editor` | Détection de génération mécanique | document-auditor |
| `document-auditor` | Audit global (lecture seule) | — |
| `document-polisher` | Dernière passe de finition | document-auditor |

### Pipeline Document Craft

```
GLOBAL_QA (pass)
    → CRAFT_TASTE         (direction de design)
    → CRAFT_TYPOGRAPHY    (optimisation typographique)
    → CRAFT_HIERARCHY     (hiérarchie visuelle)
    → CRAFT_RHYTHM        (rythme documentaire)
    → CRAFT_COMPOSITION   (composition des pages)
    → CRAFT_HUMAN_FINISH  (finition humaine)
    → CRAFT_AUDIT         (audit complet)
    → CRAFT_POLISH        (polish final)
    → EXPORT
```

### Commandes Document Craft

| Commande | Description |
|----------|-------------|
| `./run.sh craft` | Pipeline complet de qualité éditoriale |
| `./run.sh taste` | Analyse du goût éditorial |
| `./run.sh typography` | Optimisation typographique |
| `./run.sh composition` | Analyse de la composition des pages |
| `./run.sh rhythm` | Analyse du rythme documentaire |
| `./run.sh polish` | Dernière passe de finition |
| `./run.sh humanize` | Réduire les signes de génération mécanique |
| `./run.sh audit` | Audit Document Craft |
| `./run.sh visual-audit` | Export PDF + audit visuel |

### Direction de Design

Le fichier `.docforge/model/design_direction.yaml` définit la direction
éditoriale et visuelle. Il est produit par l'Art Director et lu par tous
les agents craft. Il contient : type de document, style visuel, densité,
approche typographique, philosophie d'espacement, méthode de hiérarchie,
traitement des tableaux et figures, niveau de finition.

### Adaptation au Profil Documentaire

Le moteur adapte son traitement au type de document :

| Profil | Caractéristiques |
|--------|-----------------|
| `academic` | Sobre, hiérarchique, lisible, peu décoratif |
| `corporate` | Identité visuelle contrôlée, plus de contraste |
| `technical` | Densité structurée, précision |
| `institutional` | Formel, stable |
| `editorial` | Liberté typographique |
| `minimal` | Espace, simplicité, peu d'éléments |

### Principes

1. **Intégrité du contenu** > cohérence > lisibilité > typographie > composition
2. **Séparation builder/verifier** — un agent qui corrige n'est jamais son propre vérificateur
3. **Non-invention** — jamais d'ajout de contenu, données, sources, ou citations
4. **"Humain"** = décisions intentionnelles, pas irrégulier
5. **"Impeccable"** ≠ toutes les règles vertes — un document conforme peut être éditorialement faible
6. **Chaque élément** doit avoir une fonction

## Document Safety

The system follows strict safety rules:
- Never rewrites document content
- Only applies: formatting, typography, logged language corrections
- All modifications are traceable via paragraph IDs and hashes
- Original document is never modified (only copies in `work/`)
- Integrity verification compares every paragraph before/after
