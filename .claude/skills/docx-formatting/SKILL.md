# DOCX Formatting Skill

## Trigger
Use when: a chapter or assembled document needs formatting applied.

## Standards (from config/document_config.yaml)

- Font: Times New Roman, 12pt
- Alignment: justified
- Line spacing: 1.25
- Margins: 2.5cm all sides
- Heading 1: 16pt, page break before
- Heading 2: 14pt
- Heading 3: 12pt, bold
- Page numbering: centered footer, excluded from cover page

## Process

1. Run: `cd scripts && python3 apply_styles.py <input.docx>`
2. Run: `cd scripts && python3 validate_layout.py <input.docx>`
3. If issues remain, apply targeted fixes
4. Re-validate

## Rules

- NEVER modify text content
- Only change visual formatting
- Use Python scripts for all modifications
- Report any issues that cannot be fixed automatically
