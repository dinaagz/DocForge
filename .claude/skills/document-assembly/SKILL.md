# Document Assembly Skill

## Trigger
Use when: all chapters are processed and ready for assembly.

## Process

1. Read `state/chapter_status.json` — verify all chapters are VALIDATED or PENDING_MANUAL
2. Run: `cd scripts && python3 merge_docx.py`
3. Run: `cd scripts && python3 apply_styles.py work/assembled/merged.docx`
4. Run: `cd scripts && python3 update_fields.py work/assembled/merged.docx`
5. Verify paragraph count matches expectations

## Rules

- Preserve chapter order from `state/structure_locked.json`
- Preserve all formatting
- Do NOT modify text content
- Report any PENDING_MANUAL chapters
- The assembled document goes to `work/assembled/merged.docx`
