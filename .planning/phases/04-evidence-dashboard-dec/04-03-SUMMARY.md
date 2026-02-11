---
phase: 4
plan: 3
title: "Sync-SolutionAssessments.ps1 extension for DEC dashboard feed"
status: complete
completed: 2026-02-10
files_created:
  - path: maintainers-local/solutions-staging/cross-solution-integration/scripts/powershell/Sync-SolutionAssessments.ps1
    lines: 677
    description: Compliance Dashboard sync script — queries 6 solutions, upserts assessment records, resolves Control 1.7 overlap
files_modified: []
---

# Plan 04-03 Summary: Sync-SolutionAssessments.ps1 For DEC Dashboard Feed

## Completed

### Task 1: Created Sync-SolutionAssessments.ps1 with full script structure

Created the complete Compliance Dashboard sync script:

- `#Requires -Version 7.0`
- `Sync-SolutionAssessments` function with `[CmdletBinding(SupportsShouldProcess)]`
- Parameters: `$DataverseUrl`, `$TenantId`, `$ClientId`, `$KeyVaultName`, `$CertificateThumbprint`, `$Solutions` (defaults to all 6), `$DryRun` switch
- Imports `IntegrationConfig.psm1` from same directory via `$PSScriptRoot`
- Full PowerShell help block: `.SYNOPSIS`, `.DESCRIPTION` (lists all 6 solutions with control mappings), `.PARAMETER`, `.EXAMPLE`, `.NOTES`
- Authentication via MSAL.PS — supports certificate-based and Key Vault client secret flows

### Task 2: Created per-solution processing loop

Two processing paths based on solution type:

**Standard solutions (ACV, SSC, AAM, CMM, FUS):**
1. Gets table config via `Get-SolutionTableConfig`
2. Queries primary table with today's date filter (solution-specific filter column)
3. Groups results by zone via `Group-Object -Property fsi_zone`
4. Derives status from status column via `ConvertTo-DashboardStatus`
5. Upserts assessment records for each control mapping
6. Gap-fills unassessed zones with Status 4 (Not Assessed)

**DEC-specific block (alert-severity-based):**
1. Queries `fsi_denycorrelations` with today's date filter
2. Queries `fsi_denyalerts` for severity distribution
3. Groups correlations by zone
4. For each zone, builds severity distribution hashtable: `@{ Critical=N; High=N; Warning=N; Info=N }`
5. Uses `Resolve-SeverityName` helper for option-set value mapping (matches Export-DenyEventEvidence.ps1 pattern)
6. Derives status via `ConvertTo-DashboardStatus -Solution 'DEC' -InputStatus $severityDist`
7. Upserts assessments for Controls 1.5, 1.7, 3.4 per zone
8. Notes include event count, alert count, and full severity breakdown
9. Zones with no correlations → Status 4 (Not Assessed)

### Task 3: Added Control 1.7 dual-solution overlap handling

Post-processing step after all solutions processed:
- Builds `$controlToSolutions` lookup to detect controls mapped by multiple solutions
- For Control 1.7 (ACV + DEC): queries assessment log for both solutions per zone
- Resolves to worst-case: `$resolvedStatus = ($realStatuses | Measure-Object -Maximum).Maximum`
- Status 4 (Not Assessed) is neutral — treated as no-data, does not override real assessments
- Combined notes reference both source solutions with individual status values
- Upserts the resolved status to Dataverse (overwrites individual solution records)
- Updates in-memory log entries to reflect resolved status

### Task 4: Added DryRun output

When `-DryRun` is specified:
- Per-solution summary table: solution name, controls, status derivation method, zones assessed/gap-filled
- DEC-specific fields: correlation count, alert count
- Tabular assessment record listing: Solution, Control, Zone, Status (labeled), Notes (truncated)
- Control overlap flags with source solutions and resolution method
- No writes to Dataverse

### Task 5: Added Invoke-DataverseQuery helper function

Private helper within the script:
- Parameters: `$Url`, `$Token`, `$EntitySet`, `$Filter`, `$Select`, `$OrderBy`, `$Top`
- Builds OData query URL with `$filter`, `$select`, `$orderby`, `$top` parameters
- Handles pagination via `@odata.nextLink` in a do-while loop
- Returns `[System.Collections.Generic.List[PSObject]]` data array
- Includes `Prefer: odata.include-annotations="*"` header

### Task 6: Added Invoke-AssessmentUpsert helper function

Private helper for upserting assessment records:
- Parameters: `$DataverseUrl`, `$Token`, `$ControlId`, `$Zone`, `$Status`, `$Notes`, `$AssessmentDate`
- Checks for existing same-day assessment via OData `$filter` query
- PATCH if exists (updates `fsi_controlassessmentid`), POST if new
- Writes to `fsi_controlassessments` entity set via Dataverse Web API v9.2
- Returns structured result: `[PSCustomObject]@{ ControlId; Zone; Action; Success; Error }`

## Decisions Made

- Added `Resolve-SeverityName` helper for option-set integer ↔ string mapping (reuses pattern from Export-DenyEventEvidence.ps1 for consistency)
- Used `[System.Collections.Generic.List]` for assessment log and solution summaries for efficient in-place updates during overlap resolution
- Standard solution date filters use solution-specific column names (e.g., `fsi_validation_date` for ACV) to match table schemas
- DryRun mode uses formatted table output with status labels (OK, Partial, Non-Comp, N/A)

## Artifacts

Script at `maintainers-local/solutions-staging/cross-solution-integration/scripts/powershell/Sync-SolutionAssessments.ps1` (677 lines, gitignored — staged for transfer to FSI-AgentGov-Solutions).
