---
name: "gsd:audit-milestone"
description: "Audit milestone completion against original intent before archiving"
tools: ["readFile", "listDirectory", "textSearch", "runInTerminal"]
---

<objective>
Audit the current milestone to verify all requirements are met, all phases delivered their goals, and the milestone is ready for archiving.

This is the FSI-AgentGov adapted version. All paths use `.planning/` (not `.gsd/`).
</objective>

<context>
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/STATE.md
</context>

<process>

<step name="gather_evidence">
For each phase:
1. Read VERIFICATION.md (or verify manually if missing)
2. Read all SUMMARY.md files
3. Check that success criteria from ROADMAP.md are met
</step>

<step name="check_requirements">
For each requirement in REQUIREMENTS.md:
1. Trace to implementing phase(s)
2. Verify implementation exists in codebase
3. Flag any unmet requirements
</step>

<step name="run_build_validation">
```bash
mkdocs build --strict
python scripts/verify_controls.py
```
</step>

<step name="produce_audit_report">
```markdown
## Milestone Audit: {version} — {name}

**Date:** YYYY-MM-DD
**Result:** READY TO ARCHIVE / GAPS FOUND

### Requirement Coverage
| REQ | Status | Phase | Evidence |
|-----|--------|-------|----------|
| REQ-1 | MET/UNMET | Phase X | {brief} |

### Phase Verification
| Phase | Status | Gaps |
|-------|--------|------|
| 1 | Verified | None |
| 2 | Verified | None |

### Build Status
- mkdocs build --strict: PASS/FAIL
- verify_controls.py: PASS/FAIL

### Recommendation
Archive / Fix gaps first
```
</step>

<step name="offer_next">
If ready: `/gsd:complete-milestone`
If gaps: `/gsd:plan-milestone-gaps`
</step>

</process>
