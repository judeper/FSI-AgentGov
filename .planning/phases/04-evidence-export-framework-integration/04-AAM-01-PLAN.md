---
phase: 04-evidence-export-framework-integration
plan: AAM-01
title: "Evidence export scripts (Export-AgentAccessEvidence, Get-AAMValidationResults, Test-EvidenceIntegrity)"
type: execute
wave: 1
depends_on: []
files_modified:
  - FSI-AgentGov-Solutions/agent-access-monitor/scripts/Export-AgentAccessEvidence.ps1
  - FSI-AgentGov-Solutions/agent-access-monitor/scripts/private/Get-AAMValidationResults.ps1
  - FSI-AgentGov-Solutions/agent-access-monitor/scripts/Test-EvidenceIntegrity.ps1
autonomous: true

must_haves:
  truths:
    - "Export-AgentAccessEvidence produces a JSON file with metadata, summary, validations, violations, and baselines sections"
    - "Every exported JSON file has a companion .sha256 file with standard hash format (hash  filename)"
    - "Evidence JSON includes exportedAt, solution, fromDate, toDate, recordCount, violationCount, and organizationUrl"
    - "Test-EvidenceIntegrity verifies hash matches and returns true/false"
    - "Export supports zone filtering (All/1/2/3), date range, and RunId parameters"
    - "Get-AAMValidationResults queries both fsi_accessvalidationhistory and fsi_accessviolations tables"
  artifacts:
    - path: "FSI-AgentGov-Solutions/agent-access-monitor/scripts/Export-AgentAccessEvidence.ps1"
      provides: "Main evidence export with SHA-256 hashing"
      contains: "ConvertTo-Json -Depth 10"
    - path: "FSI-AgentGov-Solutions/agent-access-monitor/scripts/private/Get-AAMValidationResults.ps1"
      provides: "Dataverse query helper for validation history and violations"
      contains: "fsi_accessvalidationhistory"
    - path: "FSI-AgentGov-Solutions/agent-access-monitor/scripts/Test-EvidenceIntegrity.ps1"
      provides: "SHA-256 hash verification"
      contains: "Get-FileHash"
  key_links:
    - from: "Export-AgentAccessEvidence.ps1"
      to: "Get-AAMValidationResults.ps1"
      via: "dot-sourced private helper"
      pattern: "Get-AAMValidationResults"
    - from: "Export-AgentAccessEvidence.ps1"
      to: "AAMClient.psm1"
      via: "module import for Connect-AAMDataverse and Get-AAMActiveBaseline"
      pattern: "Import-Module.*AAMClient"
    - from: "Export-AgentAccessEvidence.ps1"
      to: "Get-FileHash"
      via: "SHA-256 hash generation"
      pattern: "Get-FileHash.*SHA256"
    - from: "Test-EvidenceIntegrity.ps1"
      to: ".sha256 companion file"
      via: "hash comparison"
      pattern: "Get-FileHash.*-Algorithm SHA256"
---

# Plan 04-AAM-01: Evidence Export Scripts

## Goal

Create PowerShell evidence export scripts that produce JSON files with full agent access validation results and SHA-256 integrity hashes. Follows the proven ACV/SSC evidence export pattern adapted for the AAM solution's three-table Dataverse schema.

## Tasks

### Task 1: Create Get-AAMValidationResults.ps1 private helper

**File:** `agent-access-monitor/scripts/private/Get-AAMValidationResults.ps1`

A private helper that queries Dataverse `fsi_accessvalidationhistory` and `fsi_accessviolations` tables via Web API. Follows the established AAMClient.psm1 pattern for Dataverse interaction.

**Parameters:**
- `-DataverseUrl` (Mandatory, string) — Dataverse org URL
- `-AccessToken` (Mandatory, string) — Bearer token
- `-Zone` (Optional, ValidateSet 'All','1','2','3', default 'All') — filter by zone
- `-FromDate` (Optional, datetime, default: 30 days ago) — date range start
- `-ToDate` (Optional, datetime, default: now) — date range end
- `-RunId` (Optional, string) — filter to specific validation run
- `-IncludeViolations` (switch) — also query fsi_accessviolations table

**Implementation:**
1. Build OData filter for `fsi_accessvalidationhistory`:
   - Date range: `fsi_validation_time ge {FromDate} and fsi_validation_time le {ToDate}`
   - RunId: `fsi_run_id eq '{RunId}'` (if specified)
   - Zone filtering not applicable to summary records (they are aggregate)
2. Use `Invoke-RestMethod` with Authorization header (same pattern as AAMClient.psm1)
3. Query: `fsi_accessvalidationhistory?$filter={filters}&$orderby=fsi_validation_time desc&$select=fsi_name,fsi_run_id,fsi_validation_time,fsi_total_environments,fsi_compliant_count,fsi_violation_count,fsi_overall_status,fsi_summary_json`
4. Handle pagination with `@odata.nextLink` (while loop until no more pages)
5. If `-IncludeViolations`: query `fsi_accessviolations` with same date range and optional zone filter (`fsi_zone eq {zone}`)
6. Return PSCustomObject with `.Validations` and `.Violations` arrays
7. Include `#Requires -Version 7.0` and full comment-based help
8. Error handling: try/catch with informative messages for 401, 404, other HTTP errors

**Acceptance Criteria:**
- [ ] Queries fsi_accessvalidationhistory with date range and RunId filters
- [ ] Optionally queries fsi_accessviolations with zone filter
- [ ] Handles OData pagination via @odata.nextLink
- [ ] Returns structured object with .Validations and .Violations arrays
- [ ] Has #Requires -Version 7.0 and complete comment-based help

### Task 2: Create Export-AgentAccessEvidence.ps1 main export script

**File:** `agent-access-monitor/scripts/Export-AgentAccessEvidence.ps1`

Main export script that produces JSON evidence files with SHA-256 companion hashes.

**Parameters:**
- `-DataverseUrl` (Mandatory, string)
- `-TenantId` (Mandatory, string)
- `-OutputDirectory` (Mandatory, string) — directory for evidence files
- `-Zone` (Optional, ValidateSet 'All','1','2','3', default 'All') — zone filter
- `-RunId` (Optional, string) — export specific run only
- `-FromDate` (Optional, datetime, default: 30 days ago)
- `-ToDate` (Optional, datetime, default: now)
- `-IncludeBaselines` (switch) — include active baselines in export
- `-Interactive` (switch) — use interactive auth
- `-CertificateThumbprint` (Optional, string) — for service principal auth
- `-ClientId` (Optional, string) — app registration client ID

**Implementation:**
1. Import AAMClient module: `Import-Module "$PSScriptRoot/private/AAMClient.psm1" -Force`
2. Dot-source helper: `. "$PSScriptRoot/private/Get-AAMValidationResults.ps1"`
3. Authenticate — if Interactive, use MSAL.PS interactive flow; otherwise use certificate-based
4. Connect to Dataverse: `Connect-AAMDataverse -DataverseUrl $DataverseUrl -AccessToken $token`
5. Call Get-AAMValidationResults with zone/date/RunId filters and -IncludeViolations
6. If -IncludeBaselines: call `Get-AAMActiveBaseline` from AAMClient module
7. Build JSON evidence structure:
   ```json
   {
     "metadata": {
       "exportedAt": "ISO8601",
       "solution": "Agent Access Governance Monitor",
       "solutionVersion": "1.0.0",
       "fromDate": "ISO8601",
       "toDate": "ISO8601",
       "runId": "GUID or null",
       "zoneFilter": "All|1|2|3",
       "exportVersion": "1.0.0",
       "recordCount": integer,
       "violationCount": integer,
       "organizationUrl": "DataverseUrl"
     },
     "summary": {
       "overallStatus": "computed",
       "totalScans": count,
       "scansCompliant": count,
       "scansWithViolations": count,
       "totalViolations": count,
       "criticalViolations": count,
       "highViolations": count,
       "warningViolations": count
     },
     "validations": [ validation history records ],
     "violations": [ violation records ],
     "baselines": [ active baselines, if requested ]
   }
   ```
8. Convert with `ConvertTo-Json -Depth 10` (CRITICAL: not default depth 2)
9. Write to file with `Out-File -Encoding utf8` — filename: `aam-evidence-{zone}-{yyyyMMdd-HHmmss}.json`
10. Generate SHA-256: `Get-FileHash -Path $filePath -Algorithm SHA256`
11. Write companion file: `"{hash}  {filename}"` format (two spaces) to `{filename}.sha256`
12. Write summary to console and return PSCustomObject with EvidenceFile, HashFile, SHA256, RecordCount, ViolationCount, GeneratedAt

**Acceptance Criteria:**
- [ ] Produces JSON with metadata, summary, validations, violations, and baselines sections
- [ ] Uses ConvertTo-Json -Depth 10
- [ ] Generates .sha256 companion file with standard format
- [ ] Supports zone filtering and baseline inclusion
- [ ] Has #Requires -Version 7.0 and complete comment-based help
- [ ] No "ensures compliance" or "guarantees" language

### Task 3: Create Test-EvidenceIntegrity.ps1 verification utility

**File:** `agent-access-monitor/scripts/Test-EvidenceIntegrity.ps1`

Public verification script that validates SHA-256 integrity of evidence files. This follows the identical pattern from ACV/SSC Test-EvidenceIntegrity.ps1.

**Parameters:**
- `-EvidenceFilePath` (Mandatory, string) — path to evidence JSON file
- `-HashFilePath` (Optional, string) — path to .sha256 file (defaults to "{EvidenceFilePath}.sha256")
- `-Quiet` (switch) — suppress console output, return boolean only

**Implementation:**
1. Validate evidence file exists (throw if not)
2. Determine hash file path (parameter or default convention)
3. Validate hash file exists (throw if not)
4. Read expected hash from .sha256 file: parse first field (split on whitespace)
5. Compute actual hash: `(Get-FileHash -Path $EvidenceFilePath -Algorithm SHA256).Hash`
6. Compare hashes (case-insensitive)
7. If match: Write-Output verification message (unless -Quiet), return $true
8. If mismatch: Write-Warning with expected vs actual hashes, return $false

Include `#Requires -Version 5.1` (uses only basic cmdlets).

Full comment-based help with three examples:
- Single file verification
- Batch verification: `Get-ChildItem .\exports\*.json | ForEach-Object { Test-EvidenceIntegrity -EvidenceFilePath $_.FullName }`
- Quiet mode for automation

**Acceptance Criteria:**
- [ ] Uses Get-FileHash -Algorithm SHA256
- [ ] Handles missing evidence file and missing hash file with clear errors
- [ ] Returns boolean ($true/$false)
- [ ] Has #Requires -Version 5.1 and complete comment-based help with three examples

## Verification

All three scripts exist in agent-access-monitor/scripts/:
1. `Export-AgentAccessEvidence.ps1` — main export producing JSON + .sha256
2. `private/Get-AAMValidationResults.ps1` — Dataverse query helper
3. `Test-EvidenceIntegrity.ps1` — hash verification utility

## Success Criteria

- Export-AgentAccessEvidence.ps1 produces structured JSON with metadata, summary, validations, violations, baselines
- JSON uses -Depth 10 to prevent nested object truncation
- .sha256 companion file uses standard format (hash + two spaces + filename)
- Get-AAMValidationResults.ps1 queries two Dataverse tables with filtering and pagination
- Test-EvidenceIntegrity.ps1 verifies hash integrity and returns boolean
- All scripts follow established solution patterns (#Requires, comment-based help, error handling)

## Output

After completion, create `.planning/phases/04-evidence-export-framework-integration/04-AAM-01-SUMMARY.md`

Git operations: Commit to FSI-AgentGov-Solutions repository.
