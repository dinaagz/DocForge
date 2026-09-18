# Document Audit

## Trigger
- Phase: DOCUMENT_CRAFT, after all correction passes
- Explicit `docforge audit` command
- Before final polish, as the comprehensive quality gate
- When global QA requires a full document assessment

## Purpose
Systematic audit of every page and element in the document. This is the
most comprehensive quality check in the pipeline. It covers every category
of potential issue and produces a structured report with tracked anomalies.

## CRITICAL: Separation of Concerns
The agent running this audit must NEVER be the same agent that applies
corrections. The auditor is read-only. This separation ensures independent
quality assessment.

## Categories

### STRUCTURE
- Heading hierarchy correctness (no skipped levels)
- Chapter boundary coherence
- Section balance (no empty or oversized sections)
- Table of contents accuracy

### TYPOGRAPHY
- Font consistency across the document
- Size hierarchy correctness
- Weight usage appropriateness
- Kerning and tracking anomalies
- Ligature and special character handling

### SPACING
- Inter-paragraph spacing consistency
- Heading spacing (above/below) uniformity
- Section break spacing
- Table/figure spacing from body text
- List item spacing
- Margin compliance

### ALIGNMENT
- Text alignment consistency (justified, left, etc.)
- Table column alignment
- Figure and caption alignment
- Heading alignment
- Page number alignment
- Indent consistency

### DENSITY
- Page-level content density measurement
- Density variation across pages (spikes and voids)
- Content-to-whitespace ratio per page
- Overloaded pages (>85% coverage)
- Underloaded pages (<30% coverage without justification)

### HIERARCHY
- Visual hierarchy effectiveness
- Heading size progression
- Emphasis distribution (bold, italic, underline)
- Information priority reflected in visual weight
- Nesting depth appropriateness

### TABLES
- Border consistency
- Header formatting
- Cell padding uniformity
- Column width appropriateness
- Data alignment
- Table caption presence and formatting
- Table numbering continuity

### FIGURES
- Figure resolution adequacy
- Figure sizing appropriateness
- Figure-text proximity
- Figure numbering continuity
- Alt text or description presence

### CAPTIONS
- Caption presence for all figures and tables
- Caption formatting consistency
- Caption numbering continuity
- Caption-element proximity
- Caption content quality (descriptive, not generic)

### HEADER
- Header content correctness (chapter title, document title)
- Header formatting consistency
- First-page header treatment
- Header-body spacing

### FOOTER
- Footer content correctness
- Page number presence and format
- Footer formatting consistency
- First-page footer treatment
- Footer-body spacing

### PAGINATION
- Page numbering continuity
- Page numbering format (roman for prelims, arabic for body)
- Blank page handling
- Section start page (recto/verso)
- Orphan and widow control

### REFERENCES
- Citation format consistency
- Bibliography completeness
- Cross-reference accuracy
- Footnote formatting
- URL validity (format, not reachability)

### CONSISTENCY
- Cross-chapter formatting consistency
- Style drift detection
- Template compliance
- design_direction.yaml adherence

### VISUAL_BALANCE
- Page composition balance
- Whitespace distribution
- Element proportion
- Visual weight distribution
- Color usage balance

### HUMAN_FINISH
- Mechanical pattern detection
- Contextual variation presence
- Editorial judgment evidence
- Natural rhythm assessment

## Anomaly Schema

Each anomaly is tracked with:

```json
{
  "issue_id": "AUD-0001",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "category": "STRUCTURE|TYPOGRAPHY|SPACING|...",
  "element_id": "P000123|TBL-005|FIG-012|H1-CH03",
  "location": {
    "chapter": "CH03",
    "page": 42,
    "position": "top|middle|bottom"
  },
  "evidence": "Specific, measurable description of the issue",
  "recommendation": "Specific action to resolve the issue",
  "confidence": "HIGH|MEDIUM|LOW",
  "status": "OPEN|FIXED|ACCEPTED|WONT_FIX"
}
```

## Page-Level QA

Each page receives a quality assessment:

```json
{
  "page_id": "PAGE-042",
  "visual_density": 0.72,
  "heading_quality": "GOOD|ADEQUATE|POOR",
  "spacing_quality": "GOOD|ADEQUATE|POOR",
  "alignment_quality": "GOOD|ADEQUATE|POOR",
  "composition_quality": "GOOD|ADEQUATE|POOR",
  "problem_count": 2,
  "critical_issues": []
}
```

## Chapter-Level QA

Each chapter receives an aggregated assessment:

```json
{
  "chapter_id": "CH03",
  "total_issues": 8,
  "critical_count": 0,
  "high_count": 2,
  "medium_count": 4,
  "low_count": 2,
  "weakest_category": "SPACING",
  "strongest_category": "TYPOGRAPHY",
  "overall_grade": "A|B|C|D|F"
}
```

## Global Document QA

The document as a whole receives:

```json
{
  "agent": "document-auditor",
  "skill": "document-audit",
  "status": "COMPLETED",
  "document_grade": "A|B|C|D|F",
  "total_pages": 162,
  "total_issues": 47,
  "severity_breakdown": {
    "CRITICAL": 0,
    "HIGH": 5,
    "MEDIUM": 22,
    "LOW": 20
  },
  "category_breakdown": {
    "STRUCTURE": 2,
    "TYPOGRAPHY": 5,
    "SPACING": 8,
    "ALIGNMENT": 3,
    "DENSITY": 4,
    "HIERARCHY": 2,
    "TABLES": 6,
    "FIGURES": 3,
    "CAPTIONS": 4,
    "HEADER": 1,
    "FOOTER": 1,
    "PAGINATION": 2,
    "REFERENCES": 3,
    "CONSISTENCY": 1,
    "VISUAL_BALANCE": 1,
    "HUMAN_FINISH": 1
  },
  "chapter_grades": {},
  "page_scores": {},
  "issues": [],
  "recommendations": [],
  "verdict": "PASS|PASS_WITH_WARNINGS|NEEDS_CORRECTION|FAIL"
}
```

## Verdict Criteria

- **PASS**: 0 CRITICAL, <= 3 HIGH, document grade A or B
- **PASS_WITH_WARNINGS**: 0 CRITICAL, <= 8 HIGH, document grade B or C
- **NEEDS_CORRECTION**: Any CRITICAL, or > 8 HIGH, or document grade D
- **FAIL**: Multiple CRITICAL, or document grade F

## Rules
1. The auditor is read-only — it produces a report, never modifies the document
2. Every issue must have measurable evidence, not subjective opinion
3. Issue IDs are sequential and stable across audit iterations
4. Severity must be justified: CRITICAL means the document cannot ship as-is
5. Confidence reflects measurement certainty, not issue importance
6. Status starts as OPEN; other agents update it after corrections
7. Page-level and chapter-level QA are computed from individual issues
8. The global grade is the worst chapter grade, not the average
9. Reference design_direction.yaml for all formatting standards
10. Anomalies must be actionable — every recommendation must be specific enough to implement
