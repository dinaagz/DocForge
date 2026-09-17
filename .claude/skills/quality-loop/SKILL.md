# Quality Loop Skill

## Trigger
Use when: running QA checks on a chapter or the full document.

## Criteria

- **C1** — Content integrity (compare with original)
- **C2** — Unicode cleanliness
- **C3** — Formatting compliance
- **C4** — Structure coherence
- **C5** — Human validation points respected
- **C6** — No unverified claims added

## Loop Logic

```
PROCESS → QA → FAIL? → targeted correction → QA
                PASS? → VALIDATED
```

Maximum 5 cycles. After 5: PENDING_MANUAL.

## Process

1. Run all C1-C6 checks using Python scripts
2. If any criterion fails:
   - Identify the specific failure
   - Determine a targeted fix
   - Apply the fix
   - Re-run QA
3. Log every iteration in `state/quality_log.json`
4. Save per-chapter reports in `work/qa/`

## Rules

- Targeted corrections ONLY — never bulk rewrite
- Each iteration must fix a specific criterion
- Log: criterion, result, action taken
- After max iterations, mark PENDING_MANUAL and continue
