# Anti-Slop Document

## Trigger
- Phase: DOCUMENT_CRAFT, during quality assessment
- Explicit `docforge anti-slop` command
- When human-finish skill detects overall_impression of MECHANICAL or OBVIOUSLY_GENERATED
- Before final export as a formatting quality gate

## Purpose
Detect document "slop" — signs of AI-generated or generic formatting that make a
document look mass-produced rather than crafted. The fundamental principle:
**every element must have a function.** If it doesn't serve comprehension, navigation,
or hierarchy, it is slop.

## What It Detects

### Too Many Colors
- More than 3 distinct colors in body content (excluding figures and charts)
- Color applied to text that doesn't need differentiation
- Gradient or multi-color headings
- Inconsistent color application across similar elements

### Unnecessary Decorations
- Horizontal rules between every section
- Box borders around text that doesn't need containment
- Shadow effects on text or boxes
- Background shading on ordinary paragraphs

### Oversized Titles
- Title font size more than 2.5x body text
- Title taking more than 15% of page height
- Multiple levels of titles with dramatic size jumps
- Cover page titles that overwhelm rather than inform

### Useless Borders
- Borders on paragraphs or text blocks
- Full borders on tables where content is simple
- Nested borders (bordered content inside bordered sections)
- Decorative borders with no structural purpose

### Excessive Borders
- Tables with both inner and outer borders at full weight
- Every cell individually bordered when the data is simple
- Border styles mixed within a single table
- Borders heavier than necessary for the content

### Cascading Styles Without Reason
- More than 4 heading levels actively used
- Sub-sub-sub-sections that could be flattened
- Nested list levels beyond 3
- Style complexity that exceeds content complexity

### Artificial Large Spacing
- Spacing above headings greater than 2x body line spacing without cause
- Excessive paragraph gaps (more than 1.5x line height)
- Large gaps before or after tables/figures without justification
- Empty paragraphs used for spacing

### Repeated Patterns
- Every section opens with the same structural template
- All lists have the same number of items
- Every chapter has the same visual rhythm
- Paragraph lengths suspiciously uniform (standard deviation < 15%)

### Decorative Tables
- Tables used for layout rather than data
- Single-row tables as section dividers
- Tables with more formatting than content
- Tables where a simple list would suffice

### Useless Icons
- Icons before headings that add no meaning
- Bullet characters that are decorative rather than functional
- Emoji or symbols used as section markers
- Visual indicators that don't correspond to categories

### Artificially Split Sections
- Sections split into sub-sections with only 1-2 paragraphs each
- Headings followed by a single short paragraph before the next heading
- Content fragmented beyond what the subject requires
- Sections that could be merged without losing structure

### Generic Layout
- Templates applied without adaptation to content
- All pages look identical regardless of content type
- No variation between narrative, data, and reference sections
- Layout does not respond to the nature of the content

### Overdesign
- More visual elements than necessary for comprehension
- Styling that draws attention to the formatting rather than the content
- Presentation complexity exceeding content complexity
- Design choices that serve aesthetics over function

### Mechanical Uniformity
- Every element of a type treated identically regardless of context
- No variation in treatment between different document sections
- Formatting that ignores the semantic weight of content
- Absence of editorial judgment in styling decisions

## Document AI Tells Catalog

### Textual Tells
- **Em-dash overuse**: More than 2 em-dashes per page average
- **Uniform paragraph lengths**: Standard deviation of paragraph word counts < 15%
- **Filler language**: Phrases like "leverage", "synergize", "in order to", "it is important to note", "it should be noted that", "as previously mentioned"
- **Generic placeholder names**: Overuse of "the organization", "the stakeholders", "the system" without specifics
- **Systematic transitional phrases**: Every paragraph opens with "Furthermore", "Moreover", "Additionally", "In addition"
- **Hedging uniformity**: Every claim qualified with "may", "could", "potentially" at the same rate
- **List introduction formula**: Every list preceded by "The following X are:" or "X include:"

### Structural Tells
- **Symmetric sections**: All chapters have the same number of sub-sections
- **Template introductions**: Every chapter opens with a summary paragraph of similar length
- **Balanced conclusions**: Every section ends with a conclusion paragraph of similar length
- **Uniform heading depth**: Every chapter uses exactly the same heading levels
- **Predictable element order**: Introduction-body-conclusion repeated identically

### Visual Tells
- **Identical table styles**: No variation across tables with different purposes
- **Uniform figure sizing**: All figures the same dimensions regardless of content
- **Systematic spacing**: Every element has mathematically identical spacing
- **Grid-perfect alignment**: No natural variation in element placement
- **Homogeneous density**: Every page has the same content-to-whitespace ratio

## Pass/Fail Checklist

Each item is binary: PASS or FAIL.

| # | Check | Criterion |
|---|-------|-----------|
| 1 | Color count | <= 3 body colors (excluding figures) |
| 2 | Decoration function | Every decoration serves a structural purpose |
| 3 | Title proportion | Titles <= 2.5x body size |
| 4 | Border necessity | No borders without containment purpose |
| 5 | Style depth | No more than 4 active heading levels |
| 6 | Spacing justification | No spacing > 2x line height without cause |
| 7 | Pattern variation | No identical templates repeated > 3 times |
| 8 | Table purpose | Every table contains data, not layout |
| 9 | Icon function | Every icon/symbol maps to a meaning |
| 10 | Section minimum | Every section has >= 3 paragraphs of content |
| 11 | Em-dash density | <= 2 per page average |
| 12 | Paragraph variance | Word count std deviation >= 15% |
| 13 | Filler language | < 5 filler phrases per chapter |
| 14 | Transition variety | No transition word repeated > 3x per chapter |
| 15 | Element function | Every visual element justifies its existence |

## Output Format
```json
{
  "agent": "human-finish-editor",
  "skill": "anti-slop-document",
  "status": "COMPLETED",
  "slop_score": 0.0,
  "checklist": {
    "color_count": "PASS",
    "decoration_function": "PASS",
    "title_proportion": "PASS",
    "border_necessity": "FAIL",
    "style_depth": "PASS",
    "spacing_justification": "PASS",
    "pattern_variation": "FAIL",
    "table_purpose": "PASS",
    "icon_function": "PASS",
    "section_minimum": "PASS",
    "em_dash_density": "PASS",
    "paragraph_variance": "PASS",
    "filler_language": "PASS",
    "transition_variety": "PASS",
    "element_function": "PASS"
  },
  "issues": [
    {
      "id": "SLOP-0001",
      "category": "USELESS_BORDERS",
      "severity": "MEDIUM",
      "element_id": "TBL-005",
      "location": "Chapter 2, page 18",
      "evidence": "Full grid borders on a simple 2-column reference table",
      "recommendation": "Reduce to horizontal rules only (header and bottom)",
      "confidence": "HIGH"
    }
  ],
  "ai_tells_found": [],
  "recommendations": []
}
```

## Rules
1. Every element must justify its existence — decoration without function is slop
2. Never modify substantive content
3. Slop is cumulative: 3 minor issues may be acceptable, 15 are not
4. Context matters: a data-heavy appendix legitimately uses more tables than a narrative section
5. The goal is intentional design, not minimalism for its own sake
6. Reference design_direction.yaml for the document's intended aesthetic level
7. The slop_score is 0.0 (pristine) to 1.0 (obviously generated) — above 0.4 is a concern
8. A FAIL on any checklist item does not auto-fail the document, but the count of FAILs matters
