# Editorial Taste

## Trigger
- Phase: DOCUMENT_CRAFT or explicit `docforge taste` command
- After structure is locked and before final assembly
- When Art Director needs to establish design direction

## Purpose
Develop editorial judgment for documents. This skill evaluates whether a document
looks *intentionally composed* rather than merely *technically correct*.

## What It Analyzes

### Page-Level Composition
- Does the page feel balanced or lopsided?
- Is whitespace distributed intentionally or accidentally?
- Do elements relate to each other visually?

### Hierarchy & Proportion
- Are heading sizes proportional to their importance?
- Is there clear visual distinction between levels?
- Does the hierarchy guide the reader's eye naturally?

### Density & Breathing
- Is text density consistent across pages?
- Are there pages that feel suffocating or abandoned?
- Do transitions between sections have appropriate rhythm?

### Contrast & Emphasis
- Is emphasis used sparingly and meaningfully?
- Are bold/italic used with purpose, not habit?
- Does contrast serve comprehension?

### Restraint
- Are decorative elements justified by function?
- Are borders, colors, shading used minimally?
- Does every visual element earn its place?

### Coherence
- Do pages within a chapter look related?
- Is the visual treatment consistent across similar elements?
- Would a reader perceive this as one coherent document?

## Key Question
"Would a professional editor approve this layout, or would they
ask for another pass?"

## Output Format
```json
{
  "agent": "document-art-director",
  "skill": "editorial-taste",
  "status": "COMPLETED",
  "design_direction": ".docforge/model/design_direction.yaml",
  "assessment": {
    "overall_impression": "STRONG|ADEQUATE|WEAK",
    "dimensions": {
      "hierarchy": {"score": "A|B|C|D", "notes": "..."},
      "balance": {"score": "A|B|C|D", "notes": "..."},
      "density": {"score": "A|B|C|D", "notes": "..."},
      "contrast": {"score": "A|B|C|D", "notes": "..."},
      "restraint": {"score": "A|B|C|D", "notes": "..."},
      "coherence": {"score": "A|B|C|D", "notes": "..."}
    }
  },
  "issues": [],
  "recommendations": []
}
```

## Rules
1. Never invent or modify document content
2. Assess form, not substance
3. A technically valid document can still be editorially weak
4. "Human" means intentional, not irregular
5. Restraint is a quality, not a limitation
6. Every recommendation must reference a specific element
7. Prefer subtle improvements over dramatic changes
