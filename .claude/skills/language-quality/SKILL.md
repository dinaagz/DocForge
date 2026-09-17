# Language Quality Skill

## Trigger
Use when: processing a chapter that needs language corrections.

## Allowed

- Spelling, grammar, conjugation
- Punctuation
- French typography: guillemets « », tirets, espaces insécables
- Non-breaking spaces before : ; ! ? » and after «
- Obvious typos

## Forbidden

- Rewriting ideas or arguments
- Adding or removing content
- Modifying numbers, dates, statistics
- Modifying citations or references
- Modifying quoted text
- Vocabulary enrichment

## Process

1. Read the chapter text from the DOCX paragraphs
2. Identify corrections needed
3. For each correction, produce:
   ```json
   {
     "paragraph_id": "P000042",
     "before": "exact text",
     "after": "corrected text",
     "category": "grammar|spelling|punctuation|typography",
     "reason": "explanation"
   }
   ```
4. Save corrections to `work/chapters/{chapter_id}_corrections.json`
5. Run: `cd scripts && python3 language_diff.py <docx> --corrections <file>`

## Rules

- Minimal corrections only
- Every correction is logged
- When uncertain, flag as MANUAL_REVIEW
- Never batch-process the entire document at once
