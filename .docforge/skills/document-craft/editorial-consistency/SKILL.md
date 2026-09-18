# Editorial Consistency

## Trigger
- Phase: DOCUMENT_CRAFT, after all chapter-level processing is complete
- Explicit `docforge consistency` command
- After assembly, before final polish
- When document-audit detects CONSISTENCY category issues

## Purpose
Verify that visual treatment is consistent across the entire document.
A professionally edited document exhibits uniform formatting decisions
from the first page to the last. This skill detects "style drift" where
formatting gradually changes or varies between chapters, often because
chapters were processed independently.

## Reference
Uses `.docforge/model/design_direction.yaml` as the authoritative reference
for all formatting decisions. Every inconsistency is measured against this file.

## What It Checks

### Heading Styles Across Chapters
- H1 font, size, weight, color, spacing identical in every chapter
- H2 font, size, weight, color, spacing identical in every chapter
- H3 font, size, weight, color, spacing identical in every chapter
- Heading numbering style consistent (if used)
- Heading capitalization pattern consistent (sentence case vs. title case)
- Space above/below headings uniform across the document

### Spacing Consistency
- Paragraph spacing (before/after) uniform across chapters
- Line spacing identical across all body text
- Space between body text and headings consistent
- Space between body text and tables/figures consistent
- Section break spacing uniform
- Page break behavior consistent (e.g., H1 always starts new page, or never)

### Table Formatting Uniformity
- Table border style consistent across all tables
- Header row formatting identical (font, weight, shading, alignment)
- Cell padding uniform across tables
- Column alignment rules applied consistently
- Table caption style and position identical
- Table numbering format consistent

### Figure and Caption Treatment
- Figure alignment consistent (centered, left-aligned, etc.)
- Figure spacing (above and below) uniform
- Caption font, size, style consistent
- Caption position consistent (above or below)
- Caption numbering format consistent
- Figure reference style consistent in body text

### Font Usage Drift
- Body text font does not change between chapters
- Body text size does not change between chapters
- Emphasis styles (bold, italic) applied with consistent rules
- No unintended font substitutions or fallbacks
- Monospace/code font used consistently for technical content
- No mixed font families within the same role (e.g., two different body fonts)

### Margin Consistency
- Left, right, top, bottom margins identical across chapters
- First-page margins consistent (if different by design)
- Gutter width consistent for bound documents
- No margin drift between sections

### List Formatting
- Bullet style consistent (disc, circle, dash, etc.)
- Numbered list format consistent (1., 1), a., etc.)
- List indentation consistent at each level
- Spacing between list items uniform
- Nested list formatting consistent
- List introduction punctuation consistent (colon, period, nothing)

### Reference Style
- Citation format consistent (author-date, numbered, footnotes)
- Bibliography entry format uniform
- Cross-reference style consistent ("see Section 3.2" vs. "cf. 3.2")
- Footnote formatting consistent (size, position, numbering)
- URL formatting consistent (hyperlinked, plain text, footnoted)

## Style Drift Detection

Style drift occurs when formatting gradually changes across the document.
Common causes:
- Chapters processed by different agents or in different sessions
- Manual corrections applied inconsistently
- Copy-paste from different source documents
- Template changes mid-processing

Detection method:
1. Sample formatting properties from the first, middle, and last third of the document
2. Compare property values across samples
3. Any property that differs between samples is a drift candidate
4. Verify against design_direction.yaml to determine which value is correct

## Output Format
```json
{
  "agent": "editorial-craft-editor",
  "skill": "editorial-consistency",
  "status": "COMPLETED",
  "reference": ".docforge/model/design_direction.yaml",
  "chapters_analyzed": 12,
  "consistency_score": 0.95,
  "drift_detected": false,
  "issues": [
    {
      "id": "CON-0001",
      "category": "HEADING_STYLES",
      "severity": "HIGH",
      "element_id": "H2-CH05-003",
      "location": "Chapter 5, page 67",
      "evidence": "H2 heading uses 14pt while all other chapters use 16pt",
      "reference_value": "16pt per design_direction.yaml",
      "actual_value": "14pt",
      "first_occurrence": "Chapter 5",
      "recommendation": "Correct H2 size to 16pt in Chapter 5",
      "confidence": "HIGH"
    }
  ],
  "consistency_matrix": {
    "headings": "CONSISTENT",
    "spacing": "CONSISTENT",
    "tables": "DRIFT_DETECTED",
    "figures": "CONSISTENT",
    "fonts": "CONSISTENT",
    "margins": "CONSISTENT",
    "lists": "CONSISTENT",
    "references": "CONSISTENT"
  },
  "recommendations": []
}
```

## Rules
1. design_direction.yaml is the single source of truth for intended formatting
2. Every inconsistency must reference a specific element_id and location
3. Compare actual values against the reference, not against other chapters
4. Style drift is a pattern, not a single deviation — flag the pattern, not each instance
5. One chapter being different from all others is likely an error in that chapter
6. All chapters being slightly different from design_direction.yaml suggests a global template issue
7. Never modify substantive content
8. Consistency does not mean uniformity at all costs — design_direction.yaml may specify contextual variation
