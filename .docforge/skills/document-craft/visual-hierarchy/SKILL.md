# Visual Hierarchy

## Trigger
- Phase: DOCUMENT_CRAFT, runs in parallel with typographic-craft
- Explicit `docforge hierarchy` command

## Purpose
Verify that the visual hierarchy communicates importance correctly.
The reader should understand what is primary, secondary, and supplementary
without reading a single word.

## What It Analyzes

### Heading Hierarchy
- Do heading sizes decrease consistently with level?
- Is the size gap between levels perceptible but not dramatic?
- Are all headings of the same level visually identical?

### Element Dominance
- On any page, what draws the eye first? Is that the right element?
- Are titles the dominant element when they should be?
- Are figures and tables appropriately prominent?

### Weight Distribution
- Is bold used to mark importance or just habit?
- Are there runs of bold text that dilute its meaning?
- Is the overall weight balance appropriate for the document type?

### Position & Proximity
- Are related elements grouped visually?
- Is there clear separation between unrelated sections?
- Does proximity reflect semantic relationship?

### Reading Order
- Does the visual layout guide natural reading order?
- Are there elements that interrupt the reading flow?
- Do captions appear near their referenced figures/tables?

### Differentiation
- Can the reader distinguish body text, headings, captions,
  footnotes, and references at a glance?
- Are these distinctions consistent throughout?

## Detection Rules
- H1 size must be noticeably larger than H2 (minimum 2pt gap)
- H2 must be noticeably larger than H3 (minimum 1pt gap or weight change)
- Body text must never be confused with a heading (size + weight)
- Captions must be visually subordinate to body text
- Footnotes must be smaller than body text
- Table header rows must be visually distinct from data rows

## Output Format
```json
{
  "agent": "typographic-editor",
  "skill": "visual-hierarchy",
  "status": "COMPLETED",
  "hierarchy_map": {
    "H1": {"size_pt": 16, "bold": false, "effective_weight": "strong"},
    "H2": {"size_pt": 14, "bold": false, "effective_weight": "medium"},
    "H3": {"size_pt": 12, "bold": true, "effective_weight": "medium"},
    "body": {"size_pt": 12, "bold": false, "effective_weight": "normal"},
    "caption": {"size_pt": 10, "italic": true, "effective_weight": "light"}
  },
  "issues": [],
  "patches": []
}
```

## Rules
1. Hierarchy serves comprehension, not decoration
2. Fewer levels of distinction are better than more
3. Every element type must be distinguishable
4. Consistency within a level is mandatory
5. Reference design_direction.yaml for hierarchy approach
