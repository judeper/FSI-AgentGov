---
phase: 04-evidence-export-framework-integration
plan: SSC-01
type: execute
wave: 1
depends_on: []
files_modified:
  - FSI-AgentGov-Solutions/session-security-configurator/scripts/Export-SessionSecurityEvidence.ps1
  - FSI-AgentGov-Solutions/session-security-configurator/scripts/private/Get-SSCValidationResults.ps1
  - FSI-AgentGov-Solutions/session-security-configurator/scripts/Test-EvidenceIntegrity.ps1
autonomous: true

must_haves:
  truths:
    - "Export-SessionSecurityEvidence produces a JSON file with metadata, summary, and validations sections"
    - "Every exported JSON file has a companion .sha256 file with standard hash format"
    - "Evidence JSON includes timestamp, zone, scope, fromDate, toDate, validation results"
    - "Test-EvidenceIntegrity verifies hash matches and returns true/false"
    - "Export supports zone-specific filtering and date range parameters"
  artifacts:
    - path: "FSI-AgentGov-Solutions/session-security-configurator/scripts/Export-SessionSecurityEvidence.ps1"
      provides: "Main evidence export with SHA-256 hashing"
      contains: "ConvertTo-Json -Depth 10"
    - path: "FSI-AgentGov-Solutions/session-security-configurator/scripts/private/Get-SSCValidationResults.ps1"
      provides: "Dataverse query helper for validation history"
      contains: "fsi_ValidationHistory"
    - path: "FSI-AgentGov-Solutions/session-security-configurator/scripts/Test-EvidenceIntegrity.ps1"
      provides: "SHA-256 hash verification"
      contains: "Get-FileHash"
  key_links:
    - from: "Export-SessionSecurityEvidence.ps1"
      to: "Get-SSCValidationResults.ps1"
      via: "dot-sourced private helper"
      pattern: "Get-SSCValidationResults"
    - from: "Export-SessionSecurityEvidence.ps1"
      to: "Get-FileHash"
      via: "SHA-256 hash generation"
      pattern: "Get-FileHash.*SHA256"
    - from: "Test-EvidenceIntegrity.ps1"
      to: ".sha256 companion file"
      via: "hash comparison"
      pattern: "Get-FileHash.*-Algorithm SHA256"
---

<objective>
Create PowerShell evidence export scripts that produce JSON files with full session security validation results and SHA-256 integrity hashes.

Purpose: Compliance evidence collection for FINRA/SEC examinations requires machine-readable exports with cryptographic integrity verification. This plan delivers the evidence export pipeline (CEV-01).
Output: 3 PowerShell scripts — main export, Dataverse query helper, hash verification utility.
</objective>

<context>
Reference existing SSC solution structure:
- FSI-AgentGov-Solutions/session-security-configurator/scripts/
- Dataverse tables: fsi_SessionBaseline, fsi_ValidationHistory, fsi_DriftViolation
- Option sets: fsi_acv_zone, fsi_acv_severity, fsi_ssc_validationtype

Adapt patterns from ACV:
- Export-AuditValidationEvidence.ps1 (433 lines)
- Get-ValidationResults.ps1 (216 lines)
- Test-EvidenceIntegrity.ps1 (162 lines — copy directly)
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create Get-SSCValidationResults.ps1 private helper</name>
  <files>
    FSI-AgentGov-Solutions/session-security-configurator/scripts/private/Get-SSCValidationResults.ps1
  </files>
  <action>
    Create a private helper that queries Dataverse `fsi_ValidationHistory` table via Web API. Follow the pattern established in existing SSC private helpers (Get-DataverseThreshold.ps1).

    Parameters:
    - `-DataverseUrl` (Mandatory, string) — Dataverse org URL
    - `-AccessToken` (Optional, string) — Bearer token; if omitted, extract from current Graph context via Get-MgContext
    - `-Zone` (Optional, ValidateSet 'All','1','2','3', default 'All') — filter by zone
    - `-FromDate` (Optional, datetime, default: 30 days ago) — date range start
    - `-ToDate` (Optional, datetime, default: now) — date range end
    - `-RunId` (Optional, string) — filter to specific validation run

    Implementation:
    - Build OData filter string with zone choice values (Zone1=100000001, Zone2=100000002, Zone3=100000003)
    - Date range filter on fsi_timestamp field
    - Optional RunId filter
    - Use `Invoke-RestMethod` with Authorization header (SSC pattern from Get-DataverseThreshold.ps1)
    - Query: `fsi_validationhistories?$filter={filters}&$orderby=fsi_timestamp desc&$select=fsi_name,fsi_runid,fsi_zone,fsi_severity,fsi_validationtype,fsi_signinfequencyminutes,fsi_authstrength,fsi_requirecompliantdevice,fsi_pimintegration,fsi_breakglassstatus,fsi_conflictauditstatus,fsi_reason,fsi_timestamp`
    - Handle pagination with `@odata.nextLink` (while loop until no more pages)
    - Map option set values to readable strings before return
    - Return array of result objects
    - Include `#Requires -Version 7.0` and full comment-based help
    - Error handling: try/catch with informative messages for 401 (auth), 404 (table not found)

    Target: ~220 lines following ACV Get-ValidationResults.ps1 pattern
  </action>
  <verify>
    1. File exists at scripts/private/Get-SSCValidationResults.ps1
    2. Contains #Requires -Version 7.0
    3. Contains full comment-based help (.SYNOPSIS, .DESCRIPTION, .PARAMETER, .EXAMPLE)
    4. Contains OData query construction for fsi_ValidationHistory
    5. Contains @odata.nextLink pagination handling
    6. Contains option set value mapping
  </verify>
  <done>
    Get-SSCValidationResults.ps1 created with OData query builder, pagination handling, and option set mapping.
  </done>
</task>

<task type="auto">
  <name>Task 2: Create Export-SessionSecurityEvidence.ps1 main script</name>
  <files>
    FSI-AgentGov-Solutions/session-security-configurator/scripts/Export-SessionSecurityEvidence.ps1
  </files>
  <action>
    Create main evidence export script that produces JSON + SHA-256 hash.

    Parameters:
    - `-DataverseUrl` (Mandatory, string) — Dataverse org URL
    - `-TenantId` (Mandatory, string) — Azure AD tenant ID
    - `-Zone` (Optional, ValidateSet 'All','1','2','3', default 'All') — zone filter
    - `-OutputDirectory` (Mandatory, string) — export destination
    - `-FromDate` (Optional, datetime, default: 30 days ago)
    - `-ToDate` (Optional, datetime, default: now)
    - `-RunId` (Optional, string) — specific validation run
    - `-Interactive` (Switch) — use interactive auth
    - `-ClientId` (Optional, string) — for service principal auth
    - `-ClientSecret` (Optional, SecureString) — for service principal auth

    Implementation:
    1. Dot-source private helper: `. "$scriptRoot/private/Get-SSCValidationResults.ps1"`
    2. Authenticate to Dataverse (Interactive or Service Principal)
    3. Call Get-SSCValidationResults with parameters
    4. Build evidence object:
       ```powershell
       @{
           metadata = @{
               exportedAt     = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
               scope          = "SessionSecurity"
               zone           = $Zone
               fromDate       = $FromDate.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
               toDate         = $ToDate.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
               runId          = $RunId
               exportVersion  = "1.0.0"
               recordCount    = $results.Count
               organizationUrl = $DataverseUrl
           }
           summary = @{
               overallStatus      = # computed from severity priority
               validationsRun     = $results.Count
               validationsPassed  = ($results | Where-Object Severity -eq 'Passed').Count
               validationsFailed  = ($results | Where-Object Severity -eq 'Failed').Count
               validationsWarning = ($results | Where-Object Severity -eq 'Warning').Count
           }
           validations = $results
       }
       ```
    5. Export JSON: `ConvertTo-Json -Depth 10 | Out-File -Encoding utf8`
    6. Generate SHA-256: `Get-FileHash -Path $evidenceFilePath -Algorithm SHA256`
    7. Write companion .sha256 file: `"$($hashResult.Hash)  $fileName" | Out-File`
    8. Return summary object with file paths and hash

    File naming: `session-security-evidence-{zone}-{yyyyMMdd-HHmmss}.json`

    Include:
    - `#Requires -Version 7.0`
    - Full comment-based help with 3+ examples
    - Progress output for long operations
    - Error handling with try/catch

    Target: ~450 lines following ACV Export-AuditValidationEvidence.ps1 pattern
  </action>
  <verify>
    1. File exists at scripts/Export-SessionSecurityEvidence.ps1
    2. Contains #Requires -Version 7.0
    3. Contains ConvertTo-Json -Depth 10
    4. Contains Get-FileHash -Algorithm SHA256
    5. Produces .json and .sha256 companion files
    6. JSON structure has metadata, summary, validations sections
  </verify>
  <done>
    Export-SessionSecurityEvidence.ps1 created with full JSON export and SHA-256 integrity hashing.
  </done>
</task>

<task type="auto">
  <name>Task 3: Copy Test-EvidenceIntegrity.ps1 from ACV</name>
  <files>
    FSI-AgentGov-Solutions/session-security-configurator/scripts/Test-EvidenceIntegrity.ps1
  </files>
  <action>
    Copy Test-EvidenceIntegrity.ps1 from ACV solution — the hash verification logic is identical and reusable.

    1. Read from: FSI-AgentGov-Solutions/audit-configuration-validator/scripts/Test-EvidenceIntegrity.ps1
    2. Copy to: FSI-AgentGov-Solutions/session-security-configurator/scripts/Test-EvidenceIntegrity.ps1
    3. Update file header comment to reference SSC solution (not ACV)
    4. Keep all logic identical — SHA-256 verification is generic

    The script provides:
    - `-EvidenceFile` parameter (path to .json file)
    - `-Quiet` switch for CI/CD usage
    - Reads companion .sha256 file
    - Computes hash via Get-FileHash
    - Compares expected vs actual hash (case-insensitive)
    - Returns boolean result

    Target: ~162 lines (same as ACV version)
  </action>
  <verify>
    1. File exists at scripts/Test-EvidenceIntegrity.ps1
    2. Contains #Requires statement
    3. Contains Get-FileHash -Algorithm SHA256
    4. Header comment references Session Security Configurator
  </verify>
  <done>
    Test-EvidenceIntegrity.ps1 copied from ACV with updated header for SSC solution.
  </done>
</task>

</tasks>

<validation>
Run after all tasks complete:

```powershell
# Verify files exist
Get-ChildItem FSI-AgentGov-Solutions/session-security-configurator/scripts/Export-SessionSecurityEvidence.ps1
Get-ChildItem FSI-AgentGov-Solutions/session-security-configurator/scripts/private/Get-SSCValidationResults.ps1
Get-ChildItem FSI-AgentGov-Solutions/session-security-configurator/scripts/Test-EvidenceIntegrity.ps1

# Verify #Requires statements
Select-String -Path "FSI-AgentGov-Solutions/session-security-configurator/scripts/*.ps1" -Pattern "#Requires"

# Verify SHA-256 pattern
Select-String -Path "FSI-AgentGov-Solutions/session-security-configurator/scripts/Export-SessionSecurityEvidence.ps1" -Pattern "Get-FileHash.*SHA256"

# Verify ConvertTo-Json depth
Select-String -Path "FSI-AgentGov-Solutions/session-security-configurator/scripts/Export-SessionSecurityEvidence.ps1" -Pattern "ConvertTo-Json.*-Depth 10"
```
</validation>

<summary_template>
## Summary

- **Plan:** 04-SSC-01 Evidence Export Scripts
- **Phase:** 04-evidence-export-framework-integration
- **Wave:** 1

### Deliverables

| Artifact | Lines | Status |
|----------|-------|--------|
| Export-SessionSecurityEvidence.ps1 | ~450 | Created |
| Get-SSCValidationResults.ps1 | ~220 | Created |
| Test-EvidenceIntegrity.ps1 | ~162 | Copied from ACV |

### Must-Haves Covered

- [x] Export-SessionSecurityEvidence produces JSON + SHA-256 hash file
- [x] Evidence includes manifest with timestamp, zone, validation results
- [x] Test-EvidenceIntegrity verifies hash integrity
</summary_template>
