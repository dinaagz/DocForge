# Chapter Processing Skill

## Trigger
Use when: the loop is in CHAPTER_PROCESSING phase.

## Process

1. Read `state/chapter_status.json` to find the current chapter
2. Extract chapter paragraphs from the DOCX based on paragraph ID ranges
3. Process the chapter through:
   a. Language review (language-reviewer agent)
   b. Formatting (formatting-specialist agent)
   c. Integrity verification (integrity-verifier agent)
4. Run QA checks (quality-controller agent)

## Chapter States

- NOT_PROCESSED → PROCESSING → QA → VALIDATED
- QA failure → TARGETED_CORRECTION → QA (max 5 iterations)
- After 5 failures → PENDING_MANUAL → next chapter

## Rules

- Process ONE chapter at a time
- Update `state/chapter_status.json` after each step
- Save chapter working files in `work/chapters/{chapter_id}/`
- A chapter failure does NOT block other chapters
- Maximum 5 QA iterations per chapter
