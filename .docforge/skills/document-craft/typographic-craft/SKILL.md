# Typographic Craft

## Trigger
- Phase: DOCUMENT_CRAFT, after editorial-taste
- Explicit `docforge typography` command
- When typographic optimization is needed

## Purpose
Optimize typography beyond mechanical rule application. A correct font size
can still be visually wrong if it creates poor proportion, inadequate contrast,
or disrupted rhythm.

## What It Analyzes

### Font Choices
- Is the body font appropriate for the document type?
- Are heading fonts harmonious with body text?
- Is the font stack consistent throughout?

### Size & Scale
- Does the type scale create clear hierarchy?
- Are size jumps between levels proportional (not arbitrary)?
- Is body text sized for comfortable reading at the document's line length?

### Weight & Emphasis
- Is bold used for structure, not decoration?
- Is italic reserved for semantic emphasis (titles, foreign words, definitions)?
- Are weight transitions between heading levels smooth?

### Line Spacing (Leading)
- Does body leading allow comfortable reading?
- Is heading leading tighter than body (appropriate for display)?
- Are spacing ratios consistent across the document?

### Line Length (Measure)
- Does the text column width produce 55-75 characters per line?
- Are margins appropriate for the page size and binding?
- Is the measure consistent across sections?

### Spacing Before/After
- Is space above headings greater than space below (grouping principle)?
- Are paragraph gaps consistent?
- Do spacing values relate to the baseline grid or type size?

### Context-Dependent Rules
- A 14pt heading that technically matches config can be wrong if:
  - It's too close in size to the 12pt body (weak hierarchy)
  - The heading above is 16pt (insufficient contrast between H1/H2)
  - The paragraph below has 0 spacing (heading feels disconnected)

### Special Elements
- Table text: appropriately sized (usually 1-2pt smaller than body)
- Captions: visually distinct from body (italic, smaller, or both)
- Footnotes: proportional reduction from body
- Block quotes: indented and/or styled differently
- References: consistent formatting

## Output Format
```json
{
  "agent": "typographic-editor",
  "skill": "typographic-craft",
  "status": "COMPLETED",
  "issues": [
    {
      "id": "TYPO-0001",
      "element": "...",
      "category": "TYPOGRAPHY",
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "description": "...",
      "recommendation": "...",
      "confidence": "HIGH|MEDIUM|LOW"
    }
  ],
  "patches": []
}
```

## Rules
1. Never change text content, only its presentation
2. Context matters: a rule-compliant value can be wrong in context
3. Prefer the simplest fix that solves the problem
4. Typography serves reading, not display
5. Consistency within a level matters more than any single measurement
6. Reference design_direction.yaml for global typography approach
