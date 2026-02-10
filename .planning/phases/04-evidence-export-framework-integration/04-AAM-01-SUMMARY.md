---
phase: 04-evidence-export-framework-integration
plan: AAM-01
title: "Evidence export scripts (Export-AgentAccessEvidence, Get-AAMValidationResults, Test-EvidenceIntegrity)"
status: Complete
completed: 2026-02-09
tasks_completed: 3/3
---

# Summary 04-AAM-01: Evidence Export Scripts

## Status: Complete

All three evidence export scripts created following the proven ACV evidence export pattern, adapted for the AAM solution's three-table Dataverse schema.

## Tasks Completed

### Task 1: Get-AAMValidationResults.ps1 (Private Helper)
- **File:** `FSI-AgentGov-Solutions/agent-access-monitor/scripts/private/Get-AAMValidationResults.ps1`
- Queries `fsi_accessvalidationhistory` with date range and RunId filters
- Optionally queries `fsi_accessviolations` with zone filter via `-IncludeViolations` switch
- Handles OData pagination via `@odata.nextLink`
- Returns structured PSCustomObject with `.Validations` and `.Violations` arrays
- `#Requires -Version 7.0` with full comment-based help
- Error handling for 401, 404, and general HTTP errors

### Task 2: Export-AgentAccessEvidence.ps1 (Main Export)
- **File:** `FSI-AgentGov-Solutions/agent-access-monitor/scripts/Export-AgentAccessEvidence.ps1`
- Imports AAMClient.psm1 and dot-sources Get-AAMValidationResults.ps1
- Supports interactive (MSAL.PS) and certificate-based service principal auth
- Produces JSON with all five sections: metadata, summary, validations, violations, baselines
- Uses `ConvertTo-Json -Depth 10` to prevent nested object truncation
- Generates SHA-256 companion `.sha256` file with standard format (`hash  filename`)
- Evidence filename: `aam-evidence-{zone}-{yyyyMMdd-HHmmss}.json`
- Returns PSCustomObject with EvidenceFile, HashFile, SHA256, RecordCount, ViolationCount, GeneratedAt
- Supports zone filtering (All/1/2/3), date range, RunId, and baseline inclusion

### Task 3: Test-EvidenceIntegrity.ps1 (Verification Utility)
- **File:** `FSI-AgentGov-Solutions/agent-access-monitor/scripts/Test-EvidenceIntegrity.ps1`
- `#Requires -Version 5.1` (uses only basic cmdlets)
- Validates evidence file existence and hash file existence
- Reads expected hash, computes actual via `Get-FileHash -Algorithm SHA256`
- Case-insensitive comparison, returns `$true`/`$false`
- `-Quiet` switch for automation compatibility
- Three examples in comment-based help: single file, batch, quiet mode
- Follows ACV Test-EvidenceIntegrity.ps1 pattern exactly

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Zone filter on violations only, not validation history | Validation history records are aggregate summaries across all environments; zone filtering applies to individual violation records |
| `aam-evidence-{zone}-{yyyyMMdd-HHmmss}.json` naming | Distinguishes from ACV/SSC evidence files; includes zone for filtered exports |
| MSAL.PS for both interactive and certificate auth | Consistent with ACV pattern; supports both admin and automation scenarios |
| `#Requires -Version 7.0` for export/query, `5.1` for integrity check | Export uses PS7 features (consistent with AAMClient.psm1); integrity check is deliberately wide-compatible |
| Function wrapper in Get-AAMValidationResults | Enables dot-sourcing without side effects; matches ACV Get-ValidationResults pattern |
| Five-section JSON (metadata, summary, validations, violations, baselines) | Extends ACV three-section pattern with AAM-specific violations and baselines data |

## Files Created

| File | Full Path |
|------|-----------|
| Get-AAMValidationResults.ps1 | `FSI-AgentGov-Solutions/agent-access-monitor/scripts/private/Get-AAMValidationResults.ps1` |
| Export-AgentAccessEvidence.ps1 | `FSI-AgentGov-Solutions/agent-access-monitor/scripts/Export-AgentAccessEvidence.ps1` |
| Test-EvidenceIntegrity.ps1 | `FSI-AgentGov-Solutions/agent-access-monitor/scripts/Test-EvidenceIntegrity.ps1` |

## Dependency Graph

```
Export-AgentAccessEvidence.ps1
├── Import-Module → AAMClient.psm1 (Connect-AAMDataverse, Get-AAMActiveBaseline)
├── dot-source → Get-AAMValidationResults.ps1 (query helper)
├── MSAL.PS → Authentication (interactive or certificate)
└── Get-FileHash → SHA-256 companion file generation

Test-EvidenceIntegrity.ps1
└── Get-FileHash → SHA-256 verification (standalone, no dependencies)
```

## Commits

Files to commit in FSI-AgentGov-Solutions repository:
- `agent-access-monitor/scripts/private/Get-AAMValidationResults.ps1`
- `agent-access-monitor/scripts/Export-AgentAccessEvidence.ps1`
- `agent-access-monitor/scripts/Test-EvidenceIntegrity.ps1`
