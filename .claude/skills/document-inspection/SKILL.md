# Document Inspection Skill

## Trigger
Use when: a DOCX needs initial inspection, or when the loop state is INIT/INSPECTION.

## Process

1. Verify the input file exists in `input/`
2. Run: `cd scripts && python3 inspect_docx.py`
3. Read `state/document_manifest.json`
4. Summarize findings: paragraph count, headings, tables, images, footnotes, page breaks
5. Flag anomalies (missing heading styles, unusually long paragraphs, zero headings)

## Outputs

- `state/document_manifest.json` — full manifest with stable paragraph IDs
- `work/inspection/document_manifest.json` — copy

## Rules

- Never modify the source document
- Use stable IDs: P000001, P000002, ...
- Every paragraph gets a hash for later comparison
- Report facts, not interpretations
