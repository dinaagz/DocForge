# Human Finish

## Trigger
- Phase: DOCUMENT_CRAFT, after all formatting and composition passes
- Explicit `docforge human-finish` command
- Before final export, as the penultimate quality gate

## Purpose
Detect signs of mechanical or generic document generation and suggest fixes
for a more natural, human-finished appearance. A document that passes every
technical check can still *feel* automated. This skill identifies that gap.

## The Key Question
"Does this look like it was genuinely proofread and finalized by a human,
or like a model applied rules systematically?"

## IMPORTANT
"Human" means intentional decisions, natural hierarchy, restraint, and
context-sensitivity. It does NOT mean irregular, imperfect, or sloppy.
A human-finished document is *more* precise, not less.

## What It Analyzes

### Repetitive Patterns
- Are heading styles applied identically regardless of context?
- Do all tables use the exact same formatting with no variation?
- Are bullet lists always the same length, with the same punctuation?
- Do paragraphs exhibit suspiciously uniform length?

### Systematic Identical Styles
- Are all emphasis marks (bold, italic) applied in mechanical patterns?
- Is every heading-to-body transition identical?
- Are all captions formatted identically even when context differs?
- Do all section openings follow the same template?

### Artificial Spacing
- Is spacing between elements mathematically regular with no variation?
- Does every heading have the exact same space above and below, regardless of context?
- Are page breaks placed at perfectly regular intervals?
- Is inter-element spacing unnaturally consistent?

### Bold Overuse
- Are more than 15% of body text runs in bold?
- Are entire sentences or paragraphs bolded?
- Is bold used for emphasis more than 3 times per page on average?
- Is bold applied to items that don't warrant emphasis?

### Color Overuse
- Are more than 3 colors used in body content (excluding figures)?
- Is color used decoratively rather than functionally?
- Are headings colored when the hierarchy is already clear from size/weight?
- Is color applied inconsistently across similar elements?

### Over-Formalized Titles
- Are all titles in ALL CAPS or Title Case without variation?
- Are titles excessively long or padded with subtitles?
- Do titles include unnecessary numbering at every level?
- Are title styles heavier than content warrants?

### Uniform Tables
- Do all tables have identical column widths, borders, and shading?
- Is every table header styled the same even when table content varies?
- Are all tables the same size regardless of data?
- Is there no variation in table style between informational, data, and comparison tables?

### Functionless Decorations
- Are there horizontal rules that serve no structural purpose?
- Are borders applied to text blocks that don't need containment?
- Are icons or symbols used decoratively without meaning?
- Are shading or background colors applied without function?

### Visual Repetitions
- Does every chapter open with the same visual pattern?
- Are all page layouts structurally identical?
- Is the visual rhythm monotonous across the document?
- Do all sections end with the same pattern?

### Abrupt Transitions
- Do sections end without closure and new ones begin without context?
- Are heading jumps (H1 directly to H3) present?
- Do visual style changes happen suddenly between chapters?
- Are there jarring density changes between adjacent pages?

## Severity Scale

- **CRITICAL**: The document obviously looks auto-generated (uniform paragraph
  lengths, systematic identical formatting, no contextual variation)
- **HIGH**: Strong mechanical patterns visible to an attentive reader (bold overuse,
  repetitive table styling, functionless decorations)
- **MEDIUM**: Subtle uniformity that a professional editor would catch (spacing
  regularity, minor style repetitions)
- **LOW**: Minor polish items that improve perceived quality (slight spacing
  adjustments, minor emphasis refinements)

## Output Format
```json
{
  "agent": "human-finish-editor",
  "skill": "human-finish",
  "status": "COMPLETED",
  "overall_impression": "HUMAN_FINISHED|MOSTLY_NATURAL|MECHANICAL|OBVIOUSLY_GENERATED",
  "issues": [
    {
      "id": "HF-0001",
      "category": "REPETITIVE_PATTERNS",
      "severity": "HIGH",
      "element_id": "P000123",
      "location": "Chapter 3, page 42",
      "evidence": "All 12 tables in this chapter use identical 3-column layout with gray headers",
      "recommendation": "Vary table styling based on content type: comparison tables vs. data tables vs. reference tables",
      "confidence": "HIGH"
    }
  ],
  "statistics": {
    "bold_ratio": 0.08,
    "color_count": 2,
    "avg_paragraph_length_variance": 0.12,
    "table_style_variance": 0.0,
    "heading_pattern_score": 0.85
  },
  "recommendations": []
}
```

## Rules
1. Never modify substantive content — only formatting and presentation
2. "Human" means intentional and context-sensitive, not random or imperfect
3. Every issue must reference a specific element or location
4. Recommendations must be actionable and targeted, not vague
5. Prefer subtle refinements over dramatic changes
6. Reference design_direction.yaml for the document's intended aesthetic
7. A perfectly uniform document is a red flag, not a sign of quality
8. Context matters: technical appendices may legitimately be more uniform than narrative chapters
