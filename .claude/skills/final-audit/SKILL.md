# Final Audit Skill

## Trigger
Use when: the document is assembled and needs final global QA.

## Criteria (Global)

- **C1** — Content integrity vs original
- **C2** — Unicode cleanliness
- **C3** — Style/formatting compliance
- **C4** — Heading structure matches locked structure
- **C5** — Human validations respected
- **C6** — No unverified claims
- **C7** — Global pagination coherence
- **C8** — Visual homogeneity

## Process

1. Run all checks using Python scripts
2. If failures: targeted global corrections (max 5 iterations)
3. After max iterations: BLOCKED
4. On pass: proceed to EXPORT

## Export

1. Copy final DOCX to `output/`
2. Export PDF: `cd scripts && python3 export_pdf.py <docx>`
3. Generate report: `cd scripts && python3 generate_report.py`

## Rules

- The auditor is NOT the producer
- Maximum 5 global iterations
- All issues logged in `state/quality_log.json`
- Final report in `output/rapport_qualite.md`
