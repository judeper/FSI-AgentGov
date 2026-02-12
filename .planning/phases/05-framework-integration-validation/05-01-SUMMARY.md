---
phase: 05-framework-integration-validation
plan: 01
status: complete
started: 2026-02-12T18:00:00
completed: 2026-02-12T18:15:00
---

# Summary: Plan 05-01 — CONTROL-INDEX + Framework Count Updates + Solutions-Index

## Result: COMPLETE

All 5 tasks completed successfully. Control 1.25 added to CONTROL-INDEX, all "62 controls" → "63 controls" references updated across 17 files, and MIME Type Restrictions entry added to solutions-index.

## Tasks Completed

| # | Task | Status |
|---|------|--------|
| 1 | Add Control 1.25 to CONTROL-INDEX.md | Complete |
| 2 | Update "62 controls" → "63 controls" across docs/config | Complete |
| 3 | Update "24 security controls" → "25" and ranges 1.1-1.24 → 1.1-1.25 | Complete |
| 4 | Update "248 playbooks" → "252 playbooks" | Complete |
| 5 | Add MIME Type Restrictions to solutions-index.md | Complete |

## Commits

| Hash | Message |
|------|---------|
| e6e8d2c | docs(1.25): add Control 1.25 to CONTROL-INDEX and update control count to 63 |
| 8fc6687 | docs(1.25): update framework references for 63 controls, 25 security controls, 252 playbooks |

## Files Modified

| File | Change |
|------|--------|
| `docs/controls/CONTROL-INDEX.md` | Added 1.25 row, "62→63 Controls", "24→25 Controls" (2 locations) |
| `.github/copilot-instructions.md` | "62→63 controls", "24→25 security controls", "1.1-1.24→1.1-1.25" |
| `AGENTS.md` | "62→63 controls" |
| `README.md` | "62→63 controls", "24→25 Security Controls", "1.1-1.24→1.1-1.25", "248→252 playbooks" |
| `docs/index.md` | "62→63 controls", "24→25", "1.1-1.24→1.1-1.25" |
| `docs/getting-started/quick-start.md` | "24→25 controls" |
| `docs/getting-started/checklist.md` | "62→63 controls" |
| `docs/framework/executive-summary.md` | "24→25 controls", "62→63 controls" |
| `docs/framework/governance-fundamentals.md` | "62→63 controls", "24→25", ranges updated |
| `docs/framework/adoption-roadmap.md` | "62→63 controls" |
| `docs/framework/regulatory-framework.md` | "62→63 controls" |
| `docs/framework/solutions-integration.md` | "28 of 62 (45.2%)→29 of 63 (46.0%)", "24→25 Controls" |
| `docs/controls/pillar-1-security/index.md` | "24→25 controls" |
| `docs/playbooks/index.md` | "248→252 playbooks", "62→63 controls" |
| `docs/playbooks/control-implementations/index.md` | "24→25 controls", added 1.25 playbook row |
| `docs/reference/faq.md` | "24→25 security controls", "1.1-1.24→1.1-1.25", "62→63" |
| `docs/reference/solutions-index.md` | Added MIME Type Restrictions table row + detail section |

## Requirements Delivered

- **FRM-01:** CONTROL-INDEX.md includes Control 1.25 row; mkdocs.yml already wired (from Phase 1); all "62 controls" → "63 controls" across copilot-instructions, AGENTS.md, README, getting-started, framework docs
- **FRM-02:** solutions-index.md includes MIME Type Restrictions entry with status, components, regulatory alignment, control mappings, cross-references
