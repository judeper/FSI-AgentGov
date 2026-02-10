---
phase: 1
plan: 1
title: "Dataverse Purview Audit Deprecation"
status: complete
started: 2026-02-10
completed: 2026-02-10
---

# Summary: Plan 01-01 — Dataverse Purview Audit Deprecation

## Status: COMPLETE

## Requirements Delivered

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FCR-01 | ✅ Complete | Control 1.7 deprecation warning admonition added |
| FCR-02 | ✅ Complete | regulatory-mappings.md warnings in FINRA 4511 and SEC 17a-3/4 sections |
| FCR-03 | ✅ Complete | Controls 1.10, 2.1 reviewed — no changes needed |

## Changes Made

### Files Modified

| File | Change |
|------|--------|
| `docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md` | Added `!!! warning "Dataverse Purview Audit Event Changes — May 2026"` admonition before the Dataverse Environment-Level Audit Configuration subsection |
| `docs/reference/regulatory-mappings.md` | Added `!!! warning "Dataverse Audit Event Changes — May 2026"` in FINRA 4511 section and SEC 17a-3/4 section |

### Files Reviewed (No Changes)

| File | Finding |
|------|---------|
| `docs/controls/pillar-1-security/1.10-communication-compliance-monitoring.md` | No Dataverse audit event references — monitors M365 Copilot communication compliance through Purview |
| `docs/controls/pillar-2-management/2.1-managed-environments.md` | Only Dataverse reference is for solution deployment scripts (schema creation), not audit events |

## Decisions Made

- Used `!!! warning` instead of `!!! danger` per FSI language standards — "warning" is more appropriate for a May 2026 deadline with clear alternative guidance
- Placed the deprecation admonition BEFORE the existing Dataverse configuration subsection so readers see the warning before following configuration steps

## Verification

- `mkdocs build --strict`: PASS (zero errors)
- `python scripts/verify_controls.py`: PASS (62/62 controls valid)
- FSI language compliance: Verified — uses "may affect", "organizations should", no prohibited phrases

---
*Completed: 2026-02-10*
