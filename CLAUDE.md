# CLAUDE.md — Agentic Document Processing Loop

## System Rules (always enforced)

1. **Never rewrite a long document entirely.** All modifications are targeted, traceable, and reversible.
2. **Always use persistent state.** The truth is in `state/*.json`, never in conversation memory.
3. **Always log modifications.** Every change is recorded in `state/corrections.json` and `logs/events.jsonl`.
4. **Always use stable IDs.** Paragraphs are identified as P000001, P000002, etc. with SHA-256 hashes.
5. **Separate production from validation.** The agent that modifies content is NEVER its own quality controller.
6. **Never auto-validate human decisions.** Structure proposals require explicit human validation before proceeding.
7. **Never modify substantive content without authorization.** Only formatting, typography, and logged language corrections are allowed.
8. **Respect the 5-iteration limit.** After 5 QA failures on a chapter, mark it PENDING_MANUAL and move on.
9. **Local errors don't stop the pipeline.** A chapter failure does not block other chapters.
10. **Always support resumption.** The system must be restart-safe — state is saved after every significant step.
11. **Always produce a report.** The final quality report is generated in `output/rapport_qualite.md`.
12. **LLM output is not proof of integrity.** Always verify with deterministic scripts (compare_docx, check_unicode, validate_layout).

## Architecture Overview

```
input/         → Source DOCX
scripts/       → Deterministic Python tools (inspect, compare, format, merge, export)
.claude/agents → Specialized sub-agents (inspector, analyst, reviewer, verifier, etc.)
.claude/skills → Business rules for each processing phase
config/        → document_config.yaml (formatting rules, processing parameters)
state/         → Persistent state files (loop_state, chapter_status, corrections, etc.)
logs/          → Event journal (events.jsonl) and error logs
work/          → Working files (inspection, chapters, qa, assembled)
output/        → Final deliverables (DOCX, PDF, quality report)
```

## State Machine

```
INIT → INSPECTION → STRUCTURE_ANALYSIS → WAITING_FOR_HUMAN_VALIDATION
→ STRUCTURE_LOCKED → CHAPTER_PROCESSING → CHAPTER_QA → CHAPTER_VALIDATED
→ NEXT_CHAPTER → ASSEMBLY → GLOBAL_QA → EXPORT → FINAL_REPORT → DONE
```

## Structure Analysis = REAL Restructuring

The STRUCTURE_ANALYSIS phase does NOT just extract existing headings. It:
1. Extracts raw data (headings, paragraph content, anomalies) via `extract_structure.py`
2. **Invokes the structure-analyst agent** to propose a COMPLETE RESTRUCTURING
3. The agent analyzes document CONTENT and proposes new chapter boundaries
4. The existing numbering and heading styles are IGNORED — structure is rebuilt from scratch
5. The restructuring proposal goes to WAITING_FOR_HUMAN_VALIDATION

When running in Claude Code, Claude should automatically invoke the structure-analyst
agent when `state/structure_proposal.json` has `needs_agent_analysis: true`.

## Autonomous Execution

The loop runs autonomously from INIT to DONE with ONE pause:
- **WAITING_FOR_HUMAN_VALIDATION**: The human reviews the restructuring proposal
- Everything else (formatting, QA, corrections, assembly, export) runs without intervention
- QA checks run inline via Python scripts, auto-correct on failure, max 5 iterations per chapter

## Commands

```bash
./run.sh status     # Show current state
./run.sh run        # Run autonomously (stops only for human validation)
./run.sh resume     # Alias for run
./run.sh validate   # Validate restructuring proposal
./run.sh loop       # Continuous heartbeat
./run.sh reset --force  # Reset workflow
```

## Working With This System

- Place the input DOCX in `input/`
- Run `./run.sh run` to start — the loop runs autonomously to WAITING_FOR_HUMAN_VALIDATION
- The structure-analyst agent proposes a complete restructuring (not a mirror of existing structure)
- Review the restructuring proposal in `work/inspection/structure_proposal.md`
- Run `./run.sh validate` to approve the restructuring
- Run `./run.sh run` again — the loop runs autonomously to DONE
- Check status anytime with `./run.sh status`

## Adding New Skills

Create `.claude/skills/<skill-name>/SKILL.md` with trigger conditions, process steps, and rules.

## Adding New Agents

Create `.claude/agents/<agent-name>.md` with frontmatter (name, description, model, tools) and instructions.

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
