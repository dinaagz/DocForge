# Page Composition

## Trigger
- Phase: DOCUMENT_CRAFT, after assembly
- Explicit `docforge composition` command
- PDF visual audit phase

## Purpose
Evaluate each page as a visual composition. A well-composed page has
balanced elements, appropriate whitespace, and no layout accidents.

## What It Analyzes

### Balance
- Is the page top-heavy or bottom-heavy?
- Is content centered or skewed to one side?
- Do margins create a stable frame?

### Whitespace
- Is whitespace distributed intentionally?
- Are there large unexplained voids?
- Is there adequate breathing room around headings?

### Element Placement
- Are figures and tables well-positioned?
- Do captions sit close to their elements?
- Are block quotes properly indented and spaced?

### Alignment
- Are all elements aligned to consistent margins?
- Are indents consistent?
- Do table columns align logically?

### Page Breaks
- Do headings appear at the bottom of a page without text below? (orphan heading)
- Do single lines appear at the top of a page separated from their paragraph? (widow)
- Are page breaks placed at logical section boundaries?

### Density
- Is the page's content-to-whitespace ratio appropriate?
- Are there pages with more than 85% text coverage? (too dense)
- Are there pages with less than 30% text coverage without justification?

## Defect Catalog

### Critical
- `orphan_heading`: heading at page bottom with no content below
- `table_split`: table split across pages when it could fit on one
- `figure_displacement`: figure far from its text reference

### High
- `oversized_table`: table dominating more than 80% of page
- `excessive_whitespace`: more than 40% of page is empty without reason
- `caption_distant`: caption separated from its figure/table

### Medium
- `density_spike`: page density differs from neighbors by more than 40%
- `alignment_inconsistency`: elements not aligned to page grid
- `unbalanced_page`: content concentrated in one area

### Low
- `minor_spacing`: small spacing inconsistency
- `margin_variation`: slight margin difference between sections

## Output Format
```json
{
  "agent": "page-composer",
  "skill": "page-composition",
  "status": "COMPLETED",
  "pages_analyzed": 162,
  "issues": [
    {
      "id": "COMP-0001",
      "element": "PAGE-012",
      "category": "COMPOSITION",
      "severity": "HIGH",
      "description": "Orphan heading 'Chapitre 3' at bottom of page with no content below",
      "recommendation": "Move heading to next page",
      "confidence": "HIGH"
    }
  ],
  "page_scores": {},
  "patches": []
}
```

## Rules
1. Every page should be evaluable as a standalone composition
2. Context matters: a nearly-empty page after a chapter title is fine
3. Don't add elements to improve composition — only reposition
4. Prefer page breaks over content rearrangement
5. Tables should not be split unless they exceed one full page
6. Reference design_direction.yaml for page strategy
