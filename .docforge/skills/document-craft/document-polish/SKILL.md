# Document Polish

## Trigger
- Phase: DOCUMENT_CRAFT, as the final pass before export
- Explicit `docforge polish` command
- After document-audit verdict is PASS or PASS_WITH_WARNINGS
- Never before the audit has run

## Purpose
Final finishing pass. This skill does NOT redo the document. It searches for
remaining imperfections only — the small defects that survive all previous
passes. Think of it as the final quality inspection on an assembly line:
the product is built, this pass catches what slipped through.

## What It Searches For

### Small Misalignments
- Elements slightly off the margin grid
- Indents that differ by 1-2pt from the standard
- Table columns not aligned with their neighbors
- Figure captions slightly off-center

### Inconsistencies
- A single heading that differs from others at the same level
- One table with slightly different border weight
- A caption using a different font size than all others
- A single list using different bullet style

### Spacing Issues
- One heading with slightly more space above than its peers
- A paragraph gap that differs from the standard by a few points
- Uneven spacing around a single table or figure
- An orphan line at the top of a page

### Title Issues
- A title that wraps awkwardly across lines
- A heading that is accidentally styled differently
- A numbered heading with inconsistent numbering format
- A heading that is too close to or too far from its content

### Table Issues
- A column slightly too narrow for its content
- A cell with different padding than its neighbors
- A header row with slightly different alignment
- A table that could fit on the current page but breaks to the next

### Caption Issues
- A caption separated from its figure by too much space
- A caption with inconsistent punctuation (period vs. no period)
- A caption numbered out of sequence
- A caption using different formatting than others

### Pagination Issues
- A page with excessive blank space at the bottom
- A section that starts at the bottom of a page (should start next page)
- A heading at the very bottom of a page with no content below
- An awkward page break inside a short paragraph

### Weak Pages
- Pages with noticeably less content than their neighbors
- Pages where the composition feels unbalanced
- Pages with a single small element surrounded by whitespace
- Pages that feel incomplete or transitional without reason

### Style Variations
- Minor font size differences (e.g., 11.5pt vs. 12pt)
- Inconsistent use of smart quotes vs. straight quotes
- Mixed dash styles (en-dash vs. em-dash vs. hyphen)
- Inconsistent list termination (semicolons vs. periods vs. nothing)

### Typographic Details
- Double spaces between sentences
- Missing non-breaking spaces before punctuation (French typography)
- Incorrect quotation mark style for the document language
- Missing or inconsistent use of thin spaces
- Incorrect ellipsis characters (three periods vs. ellipsis character)

## Polish Loop

Maximum **5 iterations** in the polish loop:
1. Scan the document for remaining imperfections
2. Produce targeted patches for each issue found
3. Apply patches
4. Re-scan to verify fixes and detect any new issues introduced
5. If new issues found, repeat (up to 5 total iterations)
6. If clean scan after patches, polish is complete

After 5 iterations, any remaining issues are logged as ACCEPTED and the
document proceeds to export.

## Output Format
```json
{
  "agent": "document-polisher",
  "skill": "document-polish",
  "status": "COMPLETED",
  "iterations": 2,
  "issues_found": 14,
  "issues_fixed": 12,
  "issues_accepted": 2,
  "patches": [
    {
      "patch_id": "POL-0001",
      "element_id": "P000456",
      "location": "Chapter 4, page 55",
      "type": "SPACING",
      "description": "Heading space above 18pt, should be 16pt per design_direction.yaml",
      "before": "18pt",
      "after": "16pt",
      "status": "APPLIED"
    }
  ],
  "before_after": [
    {
      "element_id": "P000456",
      "location": "Chapter 4, page 55",
      "before_description": "H2 heading with 18pt space above, 2pt more than standard",
      "after_description": "H2 heading with 16pt space above, matching design_direction.yaml",
      "verification": "CONFIRMED"
    }
  ],
  "remaining_issues": [],
  "recommendations": []
}
```

## Rules
1. This is a finishing pass, NOT a redesign — only fix small remaining defects
2. Maximum 5 iterations in the polish loop
3. Every patch must be targeted and minimal — no broad style changes
4. Every patch must include before and after values for verification
5. Never modify substantive content
6. If a fix introduces a new problem, revert the fix and log it as ACCEPTED
7. Reference design_direction.yaml for all formatting standards
8. After 5 iterations, remaining issues become ACCEPTED, not FAILED
9. The before/after comparison plan must be verifiable by a deterministic script
10. Prefer leaving a minor imperfection over risking a cascade of changes
