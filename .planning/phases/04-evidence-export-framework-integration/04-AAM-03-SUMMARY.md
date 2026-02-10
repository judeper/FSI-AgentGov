---
phase: 04-evidence-export-framework-integration
plan: AAM-03
title: "Documentation suite (SCHEMA.md, EVIDENCE_EXPORT.md, TROUBLESHOOTING.md, README update, CHANGELOG)"
status: complete
completed: 2026-02-09
---

# Summary: 04-AAM-03 — Documentation Suite

## Status: Complete

All 5 tasks completed successfully. The Agent Access Governance Monitor now has a complete documentation suite covering Dataverse schema reference, evidence export operations, and troubleshooting.

## Tasks Completed (5/5)

### Task 1: Created docs/SCHEMA.md
- **File:** `FSI-AgentGov-Solutions/agent-access-monitor/docs/SCHEMA.md`
- Documents all 3 Dataverse tables (fsi_accessbaselines, fsi_accessvalidationhistory, fsi_accessviolations) with full column definitions
- Option sets (fsi_acv_zone, fsi_acv_severity) shared with ACV solution
- 6 environment variables (fsi_AAM_* prefix) with types, defaults, and purpose
- 3 connection references (fsi_cr_dataverse, fsi_cr_office365, fsi_cr_teams)
- ASCII entity relationship diagram showing table linkages

### Task 2: Created docs/EVIDENCE_EXPORT.md
- **File:** `FSI-AgentGov-Solutions/agent-access-monitor/docs/EVIDENCE_EXPORT.md`
- Step-by-step export instructions for interactive and service principal modes
- Zone filtering and baseline inclusion examples
- Full parameters reference table (11 parameters)
- JSON schema reference with output structure
- Verification procedures: single file, batch, and cross-platform (sha256sum)
- Recommended export schedule (monthly, quarterly, on-demand)
- Troubleshooting table for common export issues

### Task 3: Created docs/TROUBLESHOOTING.md
- **File:** `FSI-AgentGov-Solutions/agent-access-monitor/docs/TROUBLESHOOTING.md`
- 6 issue categories: Deployment, Authentication, Validation, Drift Detection, Evidence Export, Power Automate Flow
- Each category uses Issue/Cause/Resolution table format
- 26 total issues documented with specific resolutions
- Cross-references to PREREQUISITES.md, SCHEMA.md, EVIDENCE_EXPORT.md, FLOW_SETUP.md

### Task 4: Updated README.md
- **File:** `FSI-AgentGov-Solutions/agent-access-monitor/README.md`
- Added Evidence Export and Hash Verification rows to Features table
- Added Step 5 (export) and Step 6 (verify) to Quick Start code block
- Updated Solution Components tree with 3 new scripts (Export-AgentAccessEvidence.ps1, Test-EvidenceIntegrity.ps1, Get-AAMValidationResults.ps1) and 3 new docs (SCHEMA.md, EVIDENCE_EXPORT.md, TROUBLESHOOTING.md)
- Added FLOW_SETUP.md to docs tree (was missing)
- Added evidence export note to Related Controls section

### Task 5: Updated CHANGELOG.md
- **File:** `FSI-AgentGov-Solutions/agent-access-monitor/CHANGELOG.md`
- Added [1.0.0] - 2026-02-09 entry before [0.3.0]
- Three subsections: Evidence Export (3 scripts), Documentation (3 docs), Framework Integration (2 items)
- All scripts listed with descriptions and feature bullets

## Key Decisions

1. **FLOW_SETUP.md added to Solution Components tree** — It was present in the docs/ folder but missing from the README tree. Added for completeness.
2. **Shared option set documentation** — Documented fsi_acv_zone and fsi_acv_severity as shared with ACV, reflecting the actual schema design.
3. **Cross-platform verification** — Included `sha256sum -c` example in EVIDENCE_EXPORT.md for Linux/macOS audit workflows.
4. **FSI language compliance** — All documentation uses hedged language ("supports compliance with", "aids in meeting") and avoids overclaims throughout.

## Files Created/Modified

| File | Action | Description |
|------|--------|-------------|
| `docs/SCHEMA.md` | Created | Dataverse schema reference (3 tables, option sets, env vars, ERD) |
| `docs/EVIDENCE_EXPORT.md` | Created | Evidence export operations guide with verification procedures |
| `docs/TROUBLESHOOTING.md` | Created | Troubleshooting guide with 6 categories and 26 issues |
| `README.md` | Modified | Added Phase 4 features, Quick Start steps, updated component tree |
| `CHANGELOG.md` | Modified | Added [1.0.0] release entry with Phase 4 additions |
