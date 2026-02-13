---
phase: 5
plan: 1
title: "CONTROL-INDEX + mkdocs + 64 controls updates + solutions-index entry"
result: success
---

# Summary: 05-01 — Framework Integration & Control Count Updates

## Result

All 6 tasks completed successfully. Control 2.22 added to CONTROL-INDEX, all "63 controls" → "64 controls" references updated across 20 files, solutions-index entry added, and hardening baseline cross-references updated.

## Task Status

| # | Task | Status |
|---|------|--------|
| 1 | Add Control 2.22 to CONTROL-INDEX.md | Complete |
| 2 | Update mkdocs.yml navigation | Complete |
| 3 | Update "63 controls" → "64 controls" across docs/config | Complete |
| 4 | Add solutions-index.md catalog entry | Complete |
| 5 | Update hardening baseline cross-references | Complete |
| 6 | Update Control 3.7 cross-reference | Complete |

## Files Modified

| File | Change |
|------|--------|
| `docs/controls/CONTROL-INDEX.md` | "63→64 controls", "21→22 Management Controls", added 2.22 row, added to Pillar 2 description |
| `mkdocs.yml` | Added 2.22 nav entry (controls + 4 playbooks) |
| `.github/copilot-instructions.md` | "63→64 controls", "21→22 management", "2.1-2.21→2.1-2.22" |
| `AGENTS.md` | "63→64 controls" |
| `README.md` | "63→64 controls", "21→22 Management", "252→256 playbooks", "2.1-2.21→2.1-2.22" |
| `docs/index.md` | "63→64 controls" (×3), Pillar 2 "21→22" |
| `docs/controls/index.md` | "21→22", added 2.21+2.22 rows |
| `docs/controls/pillar-2-management/index.md` | "21→22", added 2.22 link |
| `docs/playbooks/control-implementations/index.md` | "21→22", added 2.22 row |
| `docs/getting-started/checklist.md` | "63→64 controls" |
| `docs/framework/executive-summary.md` | "63→64 Total Controls" |
| `docs/framework/governance-fundamentals.md` | "63→64 controls" (×2), "21→22" |
| `docs/framework/adoption-roadmap.md` | "63→64 controls" |
| `docs/framework/regulatory-framework.md` | "63→64 controls" |
| `docs/framework/solutions-integration.md` | "29 of 63 (46.0%)→30 of 64 (46.9%)" |
| `docs/playbooks/index.md` | "252→256 playbooks", "63→64 controls" (×2) |
| `docs/reference/faq.md` | "63→64 controls" (×3), "21→22", "2.1-2.21→2.1-2.22" |
| `docs/reference/solutions-index.md` | Added Inactivity Timeout Enforcement entry (table row + detail section + version history), "63→64" in Compliance Dashboard and sample data |
| `docs/playbooks/advanced-implementations/configuration-hardening-baseline/index.md` | Section heading "Control 3.7→Controls 2.22, 3.7", item 30 Zone 3 differentiation, Related Controls header, Related Resources |
| `docs/controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md` | Inactivity timeout row cross-references 2.22 |

## Requirements Delivered

- **FRM-01:** CONTROL-INDEX.md, mkdocs.yml, all "63→64" updates, "21→22", "252→256"
- **FRM-02:** solutions-index.md entry + hardening baseline item 30 updated
