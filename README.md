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

## Document Safety

The system follows strict safety rules:
- Never rewrites document content
- Only applies: formatting, typography, logged language corrections
- All modifications are traceable via paragraph IDs and hashes
- Original document is never modified (only copies in `work/`)
- Integrity verification compares every paragraph before/after
