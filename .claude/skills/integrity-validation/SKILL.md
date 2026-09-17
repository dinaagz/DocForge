# Integrity Validation Skill

## Trigger
Use when: verifying that modifications haven't corrupted the document.

## Process

1. Run: `cd scripts && python3 compare_docx.py <original> <modified>`
2. Run: `cd scripts && python3 check_unicode.py <modified>`
3. Review each diff
4. Classify changes:
   - AUTHORIZED_STRUCTURAL: heading style changes, page breaks
   - AUTHORIZED_LANGUAGE: logged corrections
   - UNAUTHORIZED: content modifications not in corrections log
   - MANUAL_REVIEW: ambiguous changes

## Rules

- Cross-reference with `state/corrections.json` to verify authorized changes
- Any UNAUTHORIZED change = FAIL
- Any MANUAL_REVIEW item must be reported
- Unicode invisible characters must be flagged
- The verifier must NOT be the same agent that made the changes
