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

## Commands

```bash
./run.sh status     # Show current state
./run.sh run        # Execute one step
./run.sh resume     # Resume from last state
./run.sh validate   # Validate structure proposal
./run.sh loop       # Continuous heartbeat
./run.sh reset --force  # Reset workflow
```

## Working With This System

- Place the input DOCX in `input/`
- Run `./run.sh run` to start
- When state reaches WAITING_FOR_HUMAN_VALIDATION, review `work/inspection/structure_proposal.md`
- Run `./run.sh validate` to approve the structure
- Continue with `./run.sh run` or `./run.sh loop`
- Check status anytime with `./run.sh status`

## Adding New Skills

Create `.claude/skills/<skill-name>/SKILL.md` with trigger conditions, process steps, and rules.

## Adding New Agents

Create `.claude/agents/<agent-name>.md` with frontmatter (name, description, model, tools) and instructions.
