# Summary: Plan 02-02 — On-Demand Sharing Audit PowerShell Script

**Status:** Complete
**Executed:** 2026-02-12
**Duration:** ~12 minutes

## Deliverables

| File | Lines | Action | Commit |
|------|-------|--------|--------|
| `scripts/governance/Invoke-SharingAudit.ps1` | 688 | CREATE | `313159c` |

## Requirements Delivered

| Requirement | Description | Status |
|-------------|-------------|--------|
| DET-02 | On-demand audit script with 5 violation rules | ✅ Complete |

## Acceptance Criteria

- [x] Standard 7-section comment-based help header
- [x] `#Requires -Version 7.0` and `#Requires -Modules Microsoft.PowerApps.Administration.PowerShell`
- [x] `[CmdletBinding(SupportsShouldProcess)]` with WhatIf support
- [x] `-OutputFormat` (Table/JSON/Object), `-OutputPath`, `-IncludeEvidence` parameters matching hardening baseline pattern
- [x] `-HomeTenantId`, `-MaxIndividualShares`, `-ApprovedGroupIds` UASD-specific parameters
- [x] ASCII banner with solution name
- [x] `New-ViolationResult` helper producing structured violation objects
- [x] All 5 violation rules implemented with correct severity mappings
- [x] Results object with Metadata (IntegrityHash, version), Summary (counts by severity), Violations, AgentSettings
- [x] SHA-256 evidence hash computation when `-IncludeEvidence` specified
- [x] Console summary banner with pass/fail coloring
- [x] Output format switch with file export and parent directory creation
- [x] PowerShell AST parser validation: syntax OK

## Key Structural Elements

- **Header:** 7-section comment-based help with 3 examples
- **Parameters:** 7 parameters (OutputFormat, OutputPath, EnvironmentFilter, HomeTenantId, MaxIndividualShares, ApprovedGroupIds, IncludeEvidence)
- **Helper functions:** New-ViolationResult, Get-BapApiToken, Invoke-BapApi, Get-SharingScope, Get-PrincipalSummary
- **5 violation rules:**
  - ORG_WIDE_SHARING → Critical
  - PUBLIC_INTERNET_LINK → Critical
  - UNAPPROVED_GROUP → High
  - EXCESSIVE_INDIVIDUAL → Medium
  - CROSS_TENANT_ACCESS → High
- **Output:** PSCustomObject with Metadata, Summary, Violations, AgentSettings
- **Evidence:** SHA-256 integrity hash over full results JSON

## Decisions Made

- Followed `Invoke-HardeningBaselineCheck.ps1` pattern exactly (630 lines → 688 lines)
- Added `Get-PrincipalSummary` helper for human-readable principal type grouping
- Used `Get-AzAccessToken` for BAP API authentication (same as hardening baseline pattern)
- Script does NOT write to Dataverse — console/file output only (as specified)

## Discovered Work

None.
