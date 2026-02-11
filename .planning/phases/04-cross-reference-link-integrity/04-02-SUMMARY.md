---
phase: 4
plan: 2
title: "Navigation & Naming Fixes"
status: complete
started: 2026-02-11
completed: 2026-02-11
---

# Plan 04-02 Summary: Navigation & Naming Fixes

## Status: COMPLETE

## Commits

| Hash | Message |
|------|---------|
| `1ab4caa` | fix(04-02): navigation and naming fixes across playbooks and reference docs |

## Tasks Completed

### Task 1: Fix evidence-pack-assembly.md File Paths (XRL-04)

Replaced 10 broken file path references (using stale `templates/` and `specs/` prefixes) with correct relative markdown links. All target files verified to exist before linking.

| Broken Path | Corrected Link |
|------------|----------------|
| `templates/agent-inventory-entry.md` | `../agent-lifecycle/agent-inventory-entry.md` |
| `templates/action-authorization-matrix.md` | `../governance-operations/action-authorization-matrix.md` |
| `templates/per-agent-data-policy.md` | `../agent-lifecycle/per-agent-data-policy.md` |
| `templates/escalation-matrix.md` (x2) | `../governance-operations/escalation-matrix.md` |
| `templates/decision-log-schema.md` | `../governance-operations/decision-log-schema.md` |
| `specs/real-time-compliance-dashboard.md` | `../monitoring-and-validation/real-time-compliance-dashboard.md` |
| `specs/scope-creep-detection.md` | `../monitoring-and-validation/scope-creep-detection.md` |
| `templates/supply-chain-risk-register-entry.md` | `../regulatory-modules/supply-chain-risk-register-entry.md` |
| `templates/colorado-ai-impact-assessment.md` | `../regulatory-modules/colorado-ai-impact-assessment.md` |

**Note:** The plan listed 9 broken paths, but `templates/escalation-matrix.md` appeared twice (sections 4.2 and 4.7), totaling 10 actual replacements.

### Task 2: Replace Legacy "Gap N" References (XRL-05)

Replaced all 8 Gap N placeholder references across 4 files with proper markdown cross-reference links:

| File | Gap Reference | Replaced With |
|------|--------------|---------------|
| `real-time-compliance-dashboard.md` | `(Gap 2)` | Link to `decision-log-schema.md` |
| `real-time-compliance-dashboard.md` | `(Gap 3)` | Link to `scope-creep-detection.md` |
| `real-time-compliance-dashboard.md` | `(Gap 4)` | Link to `confidence-and-routing.md` |
| `scope-creep-detection.md` | `(Gap 2)` | Link to `decision-log-schema.md` |
| `scope-creep-detection.md` | `(Gap 7 dashboard feeders)` | Link to `real-time-compliance-dashboard.md` |
| `escalation-matrix.md` | `Gap 2 decision log` | Link to `decision-log-schema.md` |
| `escalation-matrix.md` | `(Gap 7)` | Link to `real-time-compliance-dashboard.md` |
| `confidence-and-routing.md` | `(tie to Gap 2 decision logs)` | Link to `decision-log-schema.md` |

Post-verification: `Get-ChildItem -Recurse docs/playbooks -Filter *.md | Select-String "Gap [0-9]"` returns 0 matches.

### Task 3: Standardize ELM Environment Group Names (XRL-06)

Updated 2 ELM files to use Control 2.2 canonical environment group naming convention:

| Zone | Old Name | New Name |
|------|----------|----------|
| Zone 1 | `FSI-Zone1-PersonalProductivity` | `FSI-Personal-Dev` |
| Zone 2 | `FSI-Zone2-TeamCollaboration` | `FSI-Team-Collaboration` |
| Zone 3 | `FSI-Zone3-EnterpriseManagedEnvironment` | `FSI-Enterprise-Production` |

Canonical names confirmed against Control 2.2 portal walkthrough (`docs/playbooks/control-implementations/2.2/portal-walkthrough.md`).

Added migration warning admonition in `implementation-provisioning.md` for existing deployments using old naming convention.

**Files updated:**
- `implementation-provisioning.md`: Variable expression (line 142), group selection table (lines 457-459), migration note added
- `labs.md`: Flow expression (lines 586-588), test data table (lines 646-648), verification checklist (line 719)

### Task 4: Verify solutions-index.md Versions (XRL-06 partial)

**Finding:** All 19 solution version numbers are internally consistent between the "Available Solutions" table and the "Version History" table.

**Correction made:** Footer version string was `v1.2.40` but framework canonical version is `v1.2.38` (per AGENTS.md and copilot-instructions.md). Corrected to `v1.2.38`.

### Task 5: Validation

- `mkdocs build --strict` — exit code 0, documentation built in ~80 seconds
- `python scripts/verify_controls.py` — 62/62 controls pass, anchor validation pass
- No new warnings introduced (5 pre-existing INFO messages about excluded pages)

## File Manifest

| Action | File | Changes |
|--------|------|---------|
| MODIFIED | `docs/playbooks/compliance-and-audit/evidence-pack-assembly.md` | 10 broken paths → markdown links |
| MODIFIED | `docs/playbooks/monitoring-and-validation/real-time-compliance-dashboard.md` | 3 Gap N → links |
| MODIFIED | `docs/playbooks/monitoring-and-validation/scope-creep-detection.md` | 2 Gap N → links |
| MODIFIED | `docs/playbooks/governance-operations/escalation-matrix.md` | 2 Gap N → links |
| MODIFIED | `docs/playbooks/advanced-implementations/confidence-and-routing.md` | 1 Gap N → link |
| MODIFIED | `docs/playbooks/advanced-implementations/environment-lifecycle-management/implementation-provisioning.md` | ELM names + migration note |
| MODIFIED | `docs/playbooks/advanced-implementations/environment-lifecycle-management/labs.md` | ELM names (3 locations) |
| MODIFIED | `docs/reference/solutions-index.md` | Footer version v1.2.40 → v1.2.38 |

## Decisions Made

1. **10 vs 9 path fixes:** The plan listed 9 broken paths, but `templates/escalation-matrix.md` appeared in both section 4.2 (IDENTITY) and section 4.7 (MONITORING). Fixed all 10 occurrences.
2. **Gap N in headers:** For section headers containing Gap N references, converted the Gap reference into a linked document name within the header text (e.g., `### S2) Decision logs (Gap 2)` → `### S2) [Decision Logs](../governance-operations/decision-log-schema.md)`). This keeps the header readable while providing navigation.
3. **solutions-index.md version:** Corrected footer from v1.2.40 to v1.2.38 based on canonical version in AGENTS.md and copilot-instructions.md.
4. **Migration note placement:** Added as an MkDocs admonition warning box immediately after the group selection table in implementation-provisioning.md, where it's most visible to implementers.

## Discovered Work

- **No new broken links introduced** by these changes — all relative paths resolve correctly.
- The 5 pre-existing INFO messages about excluded pages (`CONTROL-INDEX.md`, `regulatory-mappings.md`) are from pages excluded via `mkdocs.yml` `not_in_nav` configuration and are unrelated to this plan.
