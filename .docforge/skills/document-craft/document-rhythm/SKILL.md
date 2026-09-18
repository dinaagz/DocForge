# Document Rhythm

## Trigger
- Phase: DOCUMENT_CRAFT, after typographic-craft
- Explicit `docforge rhythm` command

## Purpose
Ensure the document has a natural editorial rhythm — a varied but coherent
succession of elements that keeps the reader engaged without fatigue.

## What It Analyzes

### Paragraph Length Variation
- Are all paragraphs roughly the same length? (monotonous)
- Are there extreme alternations between very short and very long? (jarring)
- Is there natural variation that feels organic?

### Section Density
- Do sections vary appropriately in length?
- Is there a section that dominates disproportionately?
- Are transitions between light and dense sections smooth?

### Element Alternation
- Is there variety in content types (text, tables, figures, lists)?
- Are long text-only stretches broken by structural elements?
- Are tables/figures clustered or distributed naturally?

### Heading Frequency
- Are headings evenly distributed or clustered?
- Are there long stretches without any heading?
- Do heading levels follow a logical sequence?

### Page Density Analysis
- Are there pages significantly denser than their neighbors?
- Are there nearly-empty pages that aren't justified (e.g., not chapter starts)?
- Is the density curve smooth across the document?

### Visual Pauses
- Do chapter transitions provide adequate visual breathing?
- Are there natural rest points for the reader?
- Is the document paced for its audience?

### Repetition Detection
- Are there repeated visual patterns that create monotony?
- Do consecutive pages look identical in structure?
- Is there enough variation to maintain reader attention?

## Metrics
- `paragraph_length_variance`: coefficient of variation of paragraph lengths
- `section_balance`: ratio of longest to shortest section
- `element_distribution`: entropy of element types across pages
- `heading_regularity`: standard deviation of gaps between headings
- `density_smoothness`: max page-to-page density change
- `monotony_score`: consecutive-page similarity index

## Output Format
```json
{
  "agent": "editorial-craft-editor",
  "skill": "document-rhythm",
  "status": "COMPLETED",
  "metrics": {},
  "issues": [
    {
      "id": "RHYTHM-0001",
      "element": "PAGES-045-060",
      "category": "RHYTHM",
      "severity": "MEDIUM",
      "description": "15 consecutive pages of dense text without any table, figure, or visual break",
      "recommendation": "Consider whether existing figures can be repositioned into this stretch",
      "confidence": "HIGH"
    }
  ],
  "patches": []
}
```

## Rules
1. Never add content to create rhythm — only reposition existing elements
2. Rhythm is about perception, not formula
3. Academic documents naturally have denser sections — don't force uniformity
4. A monotonous rhythm is a real quality issue, not a preference
5. Reference design_direction.yaml for density and spacing philosophy
