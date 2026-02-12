# Phase 2 Research: FsiMimeControl PowerShell Module & Zone Templates

**Phase:** 02-powershell-module-zone-templates
**Researched:** 2026-02-12
**Phase Goal:** Build FsiMimeControl PowerShell module with zone-based MIME configuration management via Dataverse Web API

---

## 1. Existing Codebase Patterns Analysis

### 1.1 PowerShell Module Architecture

The repo has one PowerShell module and several standalone governance scripts. Patterns are highly consistent.

**Module: CAAClient.psm1** (`scripts/private/CAAClient.psm1`)
- Module-scoped connection state: `$script:DataverseUrl`, `$script:AccessToken`, `$script:Headers`
- 8 exported functions via `Export-ModuleMember -Function @(…)`
- Connect/Get-Connection pattern for Dataverse session management
- All functions use `[CmdletBinding(SupportsShouldProcess)]` where writes occur
- OData headers: `Authorization`, `OData-MaxVersion: 4.0`, `OData-Version: 4.0`, `Accept: application/json`, `Prefer: return=representation`
- API version: `/api/data/v9.2/`
- Error handling: `try/catch` with `Write-Warning` on failure, returning `$null`
- Entity naming convention: `fsi_` prefix (e.g., `fsi_capolicybaselines`, `fsi_capolicyviolations`)

**Module manifest: conditional-access-automation.psd1** (`scripts/conditional-access-automation.psd1`)
- `PowerShellVersion = '7.0'`
- `CompatiblePSEditions = @('Core')`
- Uses `NestedModules` to load private modules
- Uses `PrivateData.PSData` for Tags, ProjectUri, ReleaseNotes
- GUID-based identification

### 1.2 Standalone Governance Scripts

Six governance scripts in `scripts/governance/` follow identical conventions:

| Script | Lines | Controls | Key Patterns |
|--------|-------|----------|--------------|
| `Invoke-HardeningBaselineCheck.ps1` | 663 | 1.7, 2.1, 3.7 | Zone thresholds, check groups, `New-CheckResult` helper |
| `restrict-agent-publishing.ps1` | 907 | 1.1, 2.1, 3.7 | 6 criteria, zone-based thresholds |
| `Test-AgentAuthConfiguration.ps1` | 1020 | 1.1 | 6 SSPM items, BAP API, baseline drift |
| `Test-ZoneAgentAccess.ps1` | 1145 | 3.8, 1.1, 2.1 | Graph API, deployment groups, drift detection |
| `Invoke-SharingAudit.ps1` | 689 | 1.1, 3.8 | BAP API, 5 violation rules |
| `Export-ViolationReport.ps1` | 684 | 1.1, 3.8 | Dataverse queries, OData pagination, CSV/JSON/Object output |

**Universal conventions observed:**

1. **Header block:** Full `<# .SYNOPSIS … .NOTES #>` comment-based help
2. **Requires statement:** `#Requires -Version 7.0` + module requirements
3. **CmdletBinding:** `[CmdletBinding(SupportsShouldProcess)]` on all scripts
4. **Parameters:** `OutputFormat` (ValidateSet Table/JSON/Object), `OutputPath`, `IncludeEvidence`, `ZoneMapping`, `EnvironmentFilter`, `BaselinePath`
5. **Error preference:** `$ErrorActionPreference = 'Stop'`
6. **Banner:** Cyan ASCII box banner at script start
7. **WhatIf pattern:** Early `ShouldProcess` gate with `Write-Verbose` preview and `return`
8. **Helper functions:** Inline (`New-CheckResult`, `Get-EnvironmentZone`, `Get-DataverseToken`, `Invoke-DataverseApi`)
9. **Results structure:** `PSCustomObject` with `Metadata`, `Summary`, `Checks`/`Records`, `Gaps` properties
10. **SHA-256 evidence:** `[System.Security.Cryptography.SHA256]::Create()` for integrity hashing
11. **Output switch:** `switch ($OutputFormat) { 'JSON' { … } 'Table' { … } 'Object' { … } }`
12. **Directory creation on export:** `Split-Path -Parent` + `Test-Path` + `New-Item -ItemType Directory`
13. **Console summary:** Cyan-bordered summary block with counts and color-coded status

### 1.3 Dataverse Web API Patterns

Two distinct Dataverse access patterns exist:

**Pattern A — Module-scoped session (CAAClient.psm1):**
- `Connect-CAADataverse` stores token/URL in `$script:` scope
- Subsequent calls use `$script:Headers` implicitly
- Good for modules with multiple related operations

**Pattern B — Per-call token (Export-ViolationReport.ps1, Invoke-HardeningBaselineCheck.ps1):**
- `Get-AzAccessToken -ResourceUrl $dataverseUrl` each time
- Direct `Invoke-RestMethod` with inline header construction
- Simpler, no state management

**API endpoint for Organization entity** (used by `Invoke-HardeningBaselineCheck.ps1`):
```
${dataverseUrl}api/data/v9.2/organizations?$select=blockedattachments,blockedmimetypes,...
```

This is the exact endpoint our module needs. The hardening baseline check already queries `blockedattachments` and `blockedmimetypes` from the Organization entity (items 28-29).

**Critical finding — Organization entity fields:**
- `blockedattachments` — semicolon-separated list of blocked file extensions
- `blockedmimetypes` — semicolon-separated list of blocked MIME types
- `allowedmimetypes` — field existence needs verification (may require custom table)

### 1.4 Zone Template Patterns

No JSON zone template files exist in the repo currently. Zone logic is implemented inline:

- `Get-EnvironmentZone` helper returns zone number from `$ZoneMapping` hashtable
- Zone thresholds are hardcoded in switch statements (e.g., audit retention: Zone 1 → 180 days, Zone 2 → 365 days, Zone 3 → 730 days)
- `ZoneMapping` parameter is consistently `[hashtable]` mapping environment names to zone numbers

### 1.5 Pester Test Patterns

**No Pester test files exist anywhere in the repository.** This module establishes the Pester testing pattern for the project.

### 1.6 Control 1.25 Phase 1 Deliverables

Phase 1 produced complete documentation with specific MIME type lists:

**Blocked file extensions (baseline):**
`exe;bat;cmd;com;vbs;js;wsf;scr;pif;msi;dll;ps1;reg;inf;hta;cpl;msp;mst`

**Blocked MIME types (Zone 2+):**
`application/x-msdownload;application/x-msdos-program;application/x-bat;application/x-cmd;application/x-vbs;application/javascript;application/x-powershell;application/x-msi`

**Allowed MIME types (Zone 2+ allowlist):**
`application/pdf;image/png;image/jpeg;image/gif;text/plain;text/csv;application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;application/vnd.openxmlformats-officedocument.wordprocessingml.document;application/vnd.openxmlformats-officedocument.presentationml.presentation`

**Cmdlet names from playbook:** `Get-FsiMimeConfig`, `Set-FsiMimeConfig`, `Test-FsiMimeCompliance`

---

## 2. Recommended Technical Approach

### 2.1 Module Structure

```
scripts/governance/
├── FsiMimeControl.psm1              # Main module — 3 exported cmdlets + 2 connection helpers
├── FsiMimeControl.Tests.ps1         # Pester test suite
└── mime-templates/
    ├── zone1.json                   # Zone 1 MIME template
    ├── zone2.json                   # Zone 2 MIME template
    └── zone3.json                   # Zone 3 MIME template
```

### 2.2 Module Design: FsiMimeControl.psm1

**Module scaffold:**
```powershell
#Requires -Version 7.0
$ErrorActionPreference = 'Stop'

# Module-scoped state (follows CAAClient.psm1 pattern)
$script:DataverseUrl = $null
$script:AccessToken = $null
$script:Headers = $null
$script:TemplateBasePath = Join-Path $PSScriptRoot 'mime-templates'
```

**Cmdlet 1 — Get-FsiMimeConfig:** Read MIME configuration from Dataverse Organization entity via Web API. Query `blockedattachments`, `blockedmimetypes`. Parse semicolon-separated strings into arrays. Return PSCustomObject with `EnvironmentId`, `BlockedExtensions`, `BlockedMimeTypes`, `AllowedMimeTypes`.

**Cmdlet 2 — Set-FsiMimeConfig:** Apply zone template or custom configuration with `-WhatIf` support. Two parameter sets: `Template` (accepts zone name, loads JSON) and `Custom` (accepts individual arrays). WhatIf shows before/after comparison. PATCH via `organizations({orgId})`.

**Cmdlet 3 — Test-FsiMimeCompliance:** Validate environment against zone requirements. Internal call to Get-FsiMimeConfig, load zone template, run 6 check sequence. Return PSCustomObject with `IsCompliant`, `Checks`, `Findings`, `Summary`.

**Connection helpers:** `Connect-FsiMimeDataverse` (sets module state) and `Get-FsiMimeConnection` (returns status). Internal `Resolve-DataverseHeaders` helper shared by all cmdlets.

### 2.3 Check Result Structure

Follow `New-CheckResult` pattern from `Invoke-HardeningBaselineCheck.ps1`:
```powershell
[PSCustomObject]@{
    CheckId  = 'MIME-01'
    Setting  = 'Blocked file extensions configured'
    Status   = 'Pass'  # Pass, Fail, Warning, Info
    Expected = '18 required extensions'
    Actual   = '18 extensions configured'
    Message  = $null
}
```

---

## 3. Zone Template Schema Design

### 3.1 Schema

```json
{
  "templateVersion": "1.0.0",
  "zone": 2,
  "zoneName": "Team Collaboration",
  "description": "...",
  "blockedExtensions": ["exe", "bat", ...],
  "blockedMimeTypes": ["application/x-msdownload", ...],
  "allowedMimeTypes": ["application/pdf", ...],
  "flags": {
    "requireServerSideValidation": false,
    "requireDlpIntegration": true,
    "requireSentinelMonitoring": false
  },
  "reviewCadence": "Monthly",
  "metadata": {
    "lastUpdated": "2026-02-12",
    "version": "1.3",
    "controlReference": "1.25"
  }
}
```

### 3.2 Zone Escalation Summary

| Property | Zone 1 | Zone 2 | Zone 3 |
|----------|--------|--------|--------|
| Blocked extensions | 44 (Microsoft defaults) | 45 (+ps1) | 57 (+PS variants, cab, gadget, etc.) |
| Blocked MIME types | 0 | 15 | 21 (+shellscript, java-archive, etc.) |
| Allowed MIME types | 0 (no restriction) | 9 (standard docs) | 10 (standard docs + TIFF) |
| requireServerSideValidation | false | false | true |
| requireDlpIntegration | false | true | true |
| requireSentinelMonitoring | false | false | true |
| Review cadence | Quarterly | Monthly | Weekly |

**Note:** Zone 1 uses the comprehensive Microsoft default list from `Invoke-HardeningBaselineCheck.ps1` (`$requiredBlockedExtensions`, 44 items), which is broader than the 18-item playbook list. The hardening baseline list should be a subset of Zone 1.

---

## 4. Pester Test Strategy

### 4.1 Test Categories (~32 tests)

| Category | Tests | Description |
|----------|-------|-------------|
| Module Loading | 3 | Import, cmdlet export verification |
| Zone Template Loading | 6 | Schema validation, escalation verification |
| Get-FsiMimeConfig | 5 | Return type, parsing, error handling |
| Set-FsiMimeConfig | 6 | WhatIf, template mode, custom mode, PATCH body |
| Test-FsiMimeCompliance | 8 | Zone 1/2/3 compliance, findings, evidence |
| Connection Management | 4 | Connect, get status, token fallback |

### 4.2 Mocking Strategy

Mock `Invoke-RestMethod` with URI-pattern matching to return appropriate Organization entity responses. Mock `Get-AzAccessToken` for token acquisition. No external API calls in tests.

---

## 5. Risks and Mitigations

| # | Risk | Impact | Mitigation |
|---|------|--------|------------|
| 1 | `allowedmimetypes` field may not exist natively in Dataverse Organization entity | High | Store allowlist in custom Dataverse table or environment variable if field unavailable. Document limitation. |
| 2 | Organization entity is singleton — PATCH requires `organizationid` GUID | Low | Query organizations first to get ID, use in PATCH URL. Standard pattern. |
| 3 | No existing Pester tests to model | Medium | Write comprehensive, well-documented tests as project template. |
| 4 | PPAC settings propagation delay (up to 15 minutes) | Low | Document in cmdlet help. Return warning about propagation time. |
| 5 | API throttling for multi-environment operations | Low | Implement `Retry-After` header handling. |

---

## 6. Dependencies

### 6.1 Runtime

| Dependency | Required | Purpose |
|------------|----------|---------|
| PowerShell 7.0+ | Yes | Core runtime |
| Az.Accounts | Recommended | Token acquisition via `Get-AzAccessToken` |
| Microsoft.PowerApps.Administration.PowerShell 2.0+ | Optional | Environment discovery |

### 6.2 Development/Test

| Dependency | Required | Purpose |
|------------|----------|---------|
| Pester 5.0+ | Yes | Test suite |

### 6.3 Internal

| File | Relationship |
|------|-------------|
| `scripts/governance/mime-templates/zone1.json` | Template data for Zone 1 |
| `scripts/governance/mime-templates/zone2.json` | Template data for Zone 2 |
| `scripts/governance/mime-templates/zone3.json` | Template data for Zone 3 |
| `scripts/governance/Invoke-HardeningBaselineCheck.ps1` | Items 28-29 validate same Dataverse fields |

---

## 7. Alignment with Hardening Baseline

`Invoke-HardeningBaselineCheck.ps1` items 28-29 already check `blockedattachments` and `blockedmimetypes`. The FsiMimeControl module is complementary:

- **Hardening baseline:** _Reads and validates_ — does not write
- **FsiMimeControl:** _Reads, writes, and validates against zone templates_

Extension/MIME type lists should be synchronized. The hardening baseline's `$requiredBlockedExtensions` (44 items) and `$requiredBlockedMimeTypes` (8 items) should be a subset of Zone 1 and Zone 2 templates respectively. Future enhancement: have the hardening baseline load expected values from zone templates to eliminate duplication.

---

*Researched: 2026-02-12*
*Source: Codebase analysis of scripts/governance/, scripts/private/, docs/controls/pillar-1-security/1.25-mime-type-restrictions.md*
