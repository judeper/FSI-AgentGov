# Requirements: v22 — Solutions Status Reconciliation

## Overview

Fix stale "Work In Progress" statuses in `docs/reference/solutions-index.md` for solutions confirmed shipped in prior milestones. Two solutions (File Upload Security Configurator, Content Moderation Governance Monitor) were shipped in v8 and v7 respectively but still show "Work In Progress" in the solutions catalog.

**Source:** Manual audit of solutions-index.md vs MILESTONES.md delivery records.

**Accuracy notes:**
- File Upload Security Configurator: shipped v8 (2026-02-10), solution folder exists in FSI-AgentGov-Solutions
- Content Moderation Governance Monitor: shipped v7 (2026-02-10), solution folder exists in FSI-AgentGov-Solutions
- Segregation of Duties Detector and RAG Source Validator remain genuinely WIP (no milestone delivery found)
- No control count, playbook count, or pillar count changes
- No new controls or solutions — status corrections only

## Requirement Categories

| Code | Category | Count |
|------|----------|-------|
| STS | Status Corrections | 2 |
| VAL | Build Validation | 1 |
| **Total** | | **3** |

## STS — Status Corrections

- [x] **STS-01:** Update `docs/reference/solutions-index.md` summary table — change File Upload Security Configurator status from "Work In Progress" to "Completed" (line 23). Add Production Ready admonition to detail section if missing.

- [x] **STS-02:** Update `docs/reference/solutions-index.md` summary table — change Content Moderation Governance Monitor status from "Work In Progress" to "Completed" (line 27). Add Production Ready admonition to detail section if missing.

## VAL — Build Validation

- [x] **VAL-01:** All validations pass — `mkdocs build --strict` zero errors/warnings, `python scripts/verify_controls.py` 71/71 controls valid, no broken internal links.

## Traceability Matrix

| Requirement | Source | Scope |
|-------------|--------|-------|
| STS-01 | MILESTONES.md v8 entry confirms shipped 2026-02-10 | solutions-index.md only |
| STS-02 | MILESTONES.md v7 entry confirms shipped 2026-02-10 | solutions-index.md only |
| VAL-01 | Standard build validation | Build check |

## Out of Scope

| Item | Reason |
|------|--------|
| Segregation of Duties Detector status | Genuinely WIP — no milestone delivery |
| RAG Source Validator status | Genuinely WIP — no milestone delivery |
| New controls or solutions | Housekeeping milestone only |
| Solution code changes | Status correction in docs only |
| solutions-integration.md updates | Separate concern |

## Priority Summary

- **P1 (3):** STS-01, STS-02, VAL-01

---
*Requirements defined: 2026-02-13*
*Milestone: v22 — Solutions Status Reconciliation*
