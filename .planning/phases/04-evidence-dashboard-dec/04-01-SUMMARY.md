---
phase: 4
plan: 1
title: "Export-DenyEventEvidence.ps1 with SHA-256 hashing and regulatory alignment"
status: complete
completed: 2026-02-10
files_created:
  - path: maintainers-local/solutions-staging/deny-event-correlation-report/scripts/private/Get-DECValidationResults.ps1
    lines: 159
    description: Dataverse query helper — queries fsi_denycorrelation, fsi_denyalert, fsi_denyevent tables
  - path: maintainers-local/solutions-staging/deny-event-correlation-report/scripts/Export-DenyEventEvidence.ps1
    lines: 278
    description: Main SHA-256 evidence export — produces 6-section JSON with regulatory alignment
  - path: maintainers-local/solutions-staging/deny-event-correlation-report/scripts/Test-EvidenceIntegrity.ps1
    lines: 134
    description: Hash verification utility — validates SHA-256 companion files
files_modified: []
---

# Plan 04-01 Summary: Export-DenyEventEvidence.ps1 with SHA-256 Hashing and Regulatory Alignment

## Completed

### Task 1: Get-DECValidationResults.ps1 (Private Helper)

Created Dataverse query helper in `private/` directory:

- `#Requires -Version 7.0`
- Imports DECClient.psm1 from same directory
- Parameters: `$DataverseUrl`, `$TenantId`, `$Zone`, `$FromDate`, `$ToDate`, `$RunId`, `$IncludeRawEvents`, `$Interactive`, `$CertificateThumbprint`, `$ClientId`
- Connects to Dataverse via `Connect-DECDataverse`
- Queries 3 tables using DECClient functions:
  - `Read-DECCorrelations` — always included (primary evidence)
  - `Read-DECAlerts` — always included (compliance status evidence)
  - `Read-DECDenyEvents` — only when `-IncludeRawEvents` (gated for file size)
- Returns `[PSCustomObject]@{ Correlations; Alerts; DenyEvents; QueryTimestamp; RunId; Zone; DateRange }`
- Zone filtering supports All, 1, 2, 3
- Date range filtering on `fsi_correlation_date`, `fsi_alert_timestamp`, `fsi_timestamp`

### Task 2: Export-DenyEventEvidence.ps1 (Main Export)

Created main export script with full CmdletBinding:

- `#Requires -Version 7.0` and `#Requires -Modules @{ ModuleName = 'MSAL.PS'; RequiredVersion = '4.37.0.0' }`
- 9-step pipeline: prepare directory → fetch data → summary statistics → regulatory alignment → assemble JSON → write file → SHA-256 hash → .sha256 companion → return result
- **Summary statistics:** totalDenyEvents, totalCorrelations, totalAlerts, alertsBySeverity (Critical/High/Warning/Info), eventsBySource (RaiTelemetry/PurviewAudit/PurviewDlp)
- **Overall status derivation:** Critical/High → "Failed", Warning → "Warning", else → "Passed"
- **Regulatory alignment mapping (EVI-02):** 6 regulations mapped:
  - FINRA 4511 (Books and Records) → denyEvents, correlations → Controls 1.7, 3.4
  - FINRA 3110 (Supervisory Systems) → correlations, alerts → Controls 1.5, 3.4
  - FINRA 25-07 (AI/ML Governance) → denyEvents, correlations → Control 1.5
  - SEC 17a-3/4 (Recordkeeping) → denyEvents → Control 1.7
  - SOX 302/404 (Internal Controls) → alerts, correlations → Control 3.4
  - GLBA 501(b) (Safeguards Rule) → denyEvents → Control 1.5
- **6-section JSON:** metadata, summary, regulatoryAlignment, correlations, alerts, denyEvents
- **File naming:** `dec-evidence-{zone}-{yyyyMMdd-HHmmss}.json`
- `ConvertTo-Json -Depth 10` prevents nested truncation
- SHA-256 via `Get-FileHash -Algorithm SHA256`
- Companion `.sha256` file format: `{HASH}  {filename}`
- Returns `[PSCustomObject]@{ EvidenceFile; HashFile; SHA256; RecordCount; AlertCount; OverallStatus; GeneratedAt; Duration }`

### Task 3: Test-EvidenceIntegrity.ps1

Created hash verification utility:

- `#Requires -Version 5.1` (lower requirement — runs on Windows PS and PS 7+)
- `Test-EvidenceIntegrity` function with CmdletBinding
- Accepts pipeline input via `ValueFromPipeline` and `ValueFromPipelineByPropertyName`
- Default hash file: `$EvidenceFile.sha256`
- Validates both evidence file and hash file existence
- Parses hash from two-space-separated format
- Computes actual SHA-256 and compares
- Returns `[PSCustomObject]@{ File; ExpectedHash; ActualHash; IsValid; Error; VerifiedAt }`
- Handles error cases: EvidenceFileNotFound, HashFileNotFound, InvalidHashFormat

## Decisions Made

- Added `OverallStatus` to the export return object (not in original plan but useful for unified evidence integration)
- Handled Dataverse option set integer values alongside string values in severity/source mapping for robustness
- Added `Error` field to Test-EvidenceIntegrity result for structured error reporting

## Artifacts

All files in `maintainers-local/solutions-staging/deny-event-correlation-report/scripts/` (gitignored — staged for transfer to FSI-AgentGov-Solutions).
