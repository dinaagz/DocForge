# Structure Analysis Skill

## Trigger
Use when: the document has been inspected and a restructuring proposal is needed.

## IMPORTANT
This is a RESTRUCTURING, not a cleanup. The goal is to rebuild the document's
heading hierarchy from scratch based on content analysis. The existing numbering
and headings are INPUT DATA, not the target structure.

## Process

1. Read `state/document_manifest.json` (full paragraph inventory)
2. Run: `cd scripts && python3 extract_structure.py` (raw extraction with content previews)
3. Read `state/structure_proposal.json` (raw extraction result)
4. Analyze the document CONTENT:
   - What is the subject matter?
   - What are the logical parts? (e.g., introduction, theory, methodology, results, discussion)
   - Which existing sections belong together thematically?
5. Propose a COMPLETELY NEW hierarchy:
   - Group existing sections into coherent chapters based on CONTENT
   - Define proper heading levels (1 = chapter, 2 = section, 3 = subsection)
   - Ensure balanced chapter sizes (~10-20 pages each)
   - Keep special sections separate (bibliography, annexes, glossary)
6. Update `state/structure_proposal.json` with `restructured_sections` array
7. Rewrite `work/inspection/structure_proposal.md` as a clear restructuring proposal

## Output Format

The `restructured_sections` array in structure_proposal.json must have:
- `id`: CH01, CH02, etc.
- `proposed_title`: descriptive title based on content
- `proposed_level`: heading level (1, 2, or 3)
- `source_sections`: indices of raw sections grouped into this chapter
- `paragraph_id`: first heading paragraph ID
- `first_paragraph_id` / `last_paragraph_id`: boundary paragraph IDs
- `confidence`: 0.0-1.0
- `justification`: why these sections are grouped this way

## Rules

- NEVER just mirror the existing heading structure
- NEVER hard-code section names — discover them from content
- Propose new chapter boundaries based on THEMATIC COHERENCE
- Each proposed chapter needs: id, paragraph_id, title, level, confidence, justification
- Flag ambiguities in a separate array
- Do NOT apply changes — only propose

## Human-in-the-Loop

The restructuring proposal MUST be validated by a human before proceeding.
The loop transitions to WAITING_FOR_HUMAN_VALIDATION and stops.
