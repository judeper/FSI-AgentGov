---
phase: 4
plan: 2
wave: 2
status: complete
completed: 2026-02-10
---

# Plan 04-02 Summary: Unified Evidence Integration and IntegrationConfig Extension

## What Was Done

Created `IntegrationConfig.psm1` from scratch at `maintainers-local/solutions-staging/cross-solution-integration/scripts/powershell/IntegrationConfig.psm1` — the centralized configuration module for all 6 FSI Agent Governance solutions and their Compliance Dashboard integration.

## File Created

| Action | File | Lines |
|--------|------|-------|
| CREATE | `maintainers-local/solutions-staging/cross-solution-integration/scripts/powershell/IntegrationConfig.psm1` | 606 |

## Functions Implemented (8)

| # | Function | Purpose |
|---|----------|---------|
| 1 | `Get-SolutionControlMapping` | Maps 6 solution IDs → control arrays (DEC → 1.5, 1.7, 3.4) |
| 2 | `Get-SolutionTableConfig` | Dataverse table configs per solution; DEC uses dual-table AlertBased derivation |
| 3 | `ConvertTo-DashboardStatus` | Translates solution-specific status → dashboard codes (1-4); DEC uses severity hashtable |
| 4 | `Get-EvidenceExportScripts` | Script paths and module dependencies per solution |
| 5 | `Get-SolutionDirectories` | Solution ID → directory name mapping |
| 6 | `Get-CanonicalZoneValue` | Normalizes zone inputs (int, string, label) → canonical '1'/'2'/'3' |
| 7 | `Get-EvidenceTypeId` | Evidence type names → Dataverse option set values |
| 8 | `Get-DashboardTableConfig` | Dashboard table names, columns, and query patterns |

## Must-Haves Addressed

| # | Requirement | Status |
|---|------------|--------|
| EVI-03 | DEC evidence registered with unified evidence export via IntegrationConfig | Complete |
| EVI-04 | IntegrationConfig.psm1 extended with DEC → Controls 1.5, 1.7, 3.4 | Complete |

## Key Design Decisions

- **Control 1.7 dual mapping:** Both ACV and DEC map to Control 1.7; documented that downstream `Sync-SolutionAssessments.ps1` should use worst-case aggregation
- **DEC StatusDerivation:** Set to `'AlertBased'` with `StatusColumn = $null` — signaling that DEC status comes from alert severity counts, not a direct column value
- **DEC dual-table structure:** `fsi_denycorrelations` (primary) + `fsi_denyalerts` (alert table) with separate query patterns
- **ConvertTo-DashboardStatus DEC logic:** Critical/High → 3 (Non-Compliant), Warning → 2 (Partial), Info/none → 1 (Compliant)

## Dependencies

- **Upstream:** Plan 04-01 (Export-DenyEventEvidence.ps1) — referenced in `Get-EvidenceExportScripts`
- **Downstream:** Plan 04-03 (Sync-SolutionAssessments.ps1) — consumes all 8 functions
