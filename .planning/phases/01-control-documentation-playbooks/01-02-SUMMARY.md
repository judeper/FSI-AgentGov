---
phase: 1
plan: 2
title: "Playbooks and screenshot specification"
status: completed
completed: 2026-02-12
---

# Summary 01-02: Playbooks & Screenshot Specification

## Result

**Status:** Completed
**Deliverables:** 4 playbooks + 1 EXPECTED.md (5 files total)

## What Was Done

Created all 5 Phase 1 Plan 02 deliverables following established patterns from Control 2.21 exemplar playbooks. Each playbook uses the standard title format, metadata fields, prerequisite checkboxes, step numbering, and cross-linking to sibling playbooks.

### Deliverable Details

| File | Content Summary |
|------|----------------|
| `docs/playbooks/control-implementations/2.22/portal-walkthrough.md` | 7-step PPAC Privacy + Security walkthrough; zone-based governance settings tracker table; post-configuration Dataverse and flow validation steps |
| `docs/playbooks/control-implementations/2.22/powershell-setup.md` | Set-InactivityTimeout.ps1 parameter table (10 params); 4 example commands (WhatIf, single, bulk CSV, bulk WhatIf); GET/PATCH API reference; authentication setup; error table (401/403/404/429) |
| `docs/playbooks/control-implementations/2.22/verification-testing.md` | 6 test cases (TC-2.22-01 through TC-2.22-06); evidence checklist (6 items); attestation template |
| `docs/playbooks/control-implementations/2.22/troubleshooting.md` | 8 common issues with symptoms + resolution steps; escalation path (L1-L4); 4 known limitations table; 2 diagnostic PowerShell commands |
| `docs/images/2.22/EXPECTED.md` | 4 screenshot specifications: PPAC Privacy + Security page, timeout toggle/duration, Dataverse compliance records, notification email |

### Acceptance Criteria Verification

**Portal Walkthrough (Task 1):**

| # | Criterion | Met |
|---|-----------|-----|
| 1 | PPAC Privacy + Security navigation path | ✅ |
| 2 | 7 configuration steps | ✅ |
| 3 | Governance settings tracker table | ✅ |
| 4 | Zone-based duration requirements | ✅ |

**PowerShell Setup (Task 2):**

| # | Criterion | Met |
|---|-----------|-----|
| 1 | Set-InactivityTimeout.ps1 parameter table | ✅ |
| 2 | Example commands (WhatIf, single, bulk) | ✅ |
| 3 | -WhatIf preview support documented | ✅ |
| 4 | Bulk remediation from CSV | ✅ |
| 5 | API reference (GET/PATCH endpoints) | ✅ |

**Verification Testing (Task 3):**

| # | Criterion | Met |
|---|-----------|-----|
| 1 | 6 test cases (TC-2.22-01 through TC-2.22-06) | ✅ |
| 2 | Compliant detection test | ✅ |
| 3 | Non-compliant (exceeds max) test | ✅ |
| 4 | Non-compliant (disabled) test | ✅ |
| 5 | Unknown (missing policy) test | ✅ |
| 6 | WhatIf + Apply remediation tests | ✅ |
| 7 | Evidence checklist | ✅ |
| 8 | Attestation template | ✅ |

**Troubleshooting (Task 4):**

| # | Criterion | Met |
|---|-----------|-----|
| 1 | 8 common issues table | ✅ |
| 2 | Escalation path (L1-L4) | ✅ |
| 3 | Known limitations table | ✅ |
| 4 | Diagnostic commands | ✅ |

**EXPECTED.md (Task 5):**

| # | Criterion | Met |
|---|-----------|-----|
| 1 | 4 screenshot specifications | ✅ |
| 2 | Portal paths documented | ✅ |
| 3 | "What to capture" descriptions | ✅ |

## Dependencies

- None (Wave 1)

## Key Files

- `docs/playbooks/control-implementations/2.22/portal-walkthrough.md` (CREATED)
- `docs/playbooks/control-implementations/2.22/powershell-setup.md` (CREATED)
- `docs/playbooks/control-implementations/2.22/verification-testing.md` (CREATED)
- `docs/playbooks/control-implementations/2.22/troubleshooting.md` (CREATED)
- `docs/images/2.22/EXPECTED.md` (CREATED)
