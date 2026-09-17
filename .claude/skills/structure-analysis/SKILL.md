# Structure Analysis Skill

## Trigger
Use when: the document has been inspected and structure analysis is needed.

## Process

1. Read `state/document_manifest.json`
2. Run: `cd scripts && python3 extract_structure.py`
3. Analyze the raw extraction
4. Consider:
   - Are heading levels consistent?
   - Is there an implied hierarchy from formatting (bold, caps)?
   - Are there sections without proper heading styles?
   - Is the numbering coherent?
5. Enrich `state/structure_proposal.json` with semantic analysis
6. Write `work/inspection/structure_proposal.md` as human-readable report

## Rules

- NEVER hard-code section names
- Discover structure from document content
- Each proposed section needs: id, paragraph_id, title, level, confidence, justification
- Flag ambiguities in a separate array
- Do NOT apply changes — only propose

## Human-in-the-Loop

The structure proposal MUST be validated by a human before proceeding.
The loop transitions to WAITING_FOR_HUMAN_VALIDATION and stops.
