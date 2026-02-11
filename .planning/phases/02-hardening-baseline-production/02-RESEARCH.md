# Phase 02 Research: Hardening Baseline Production

**Phase:** 02-hardening-baseline-production
**Researched:** 2026-02-11
**Status:** Complete

---

## 1. Current State Analysis

### 1.1 Hardening Baseline Document

**File:** `docs/playbooks/advanced-implementations/configuration-hardening-baseline/index.md`
**Version:** v1.0 (February 2026)
**Status:** Exists, well-structured, needs enhancement

#### What Already Exists

1. **27-item Master Configuration Hardening Checklist** organized into 6 categories:
   - Items 1–6: Agent Authentication and Access (Control 1.1)
   - Items 7–9: Audit Logging (Control 1.7)
   - Item 10: Content Moderation (Control 1.8)
   - Items 11–13: RBAC and Agent Governance (Control 1.18)
   - Items 14–17: Environment Provisioning (Control 2.1)
   - Items 18–27: AI Feature Access (Control 3.8)

2. **Review Frequency Table** with zone-specific cadence (Monthly/Bi-weekly/Weekly) and reviewer roles. Already includes evidence requirements column.

3. **Manual Attestation Procedures** with:
   - Step-by-step evidence collection template
   - Attestation record format (plaintext, not JSON)
   - Screenshot-based verification approach

4. **Integration with Existing Solutions** table referencing:
   - Audit Configuration Validator (items 7–9)
   - Environment Lifecycle Management (items 14–17)
   - Compliance Dashboard (aggregated scoring)
   - Planned Agent Security Configuration Validator (items 1–6, 10–12, 18–22)

#### Gaps Identified

| Gap | Requirement | Notes |
|-----|-------------|-------|
| **No automation feasibility column** | HBL-01 | Checklist tables have #, Setting, Portal Path, Expected Value, Severity — but no Automation Feasibility column |
| **No evidence export procedure** | HBL-03 | Manual attestation section describes *what* to capture but not *how* to export for regulatory examination |
| **No SHA-256 hash pattern** | HBL-03 | Other advanced implementations (ELM, Deny Event Correlation) use SHA-256 hashing for evidence packages; hardening baseline does not |
| **No PowerShell verification script** | HBL-02 | Document references planned solutions but has no actual runnable script |
| **Review cadence lacks detailed zone guidance** | HBL-03 | Table exists but missing escalation triggers, audit-ready cadence documentation |

### 1.2 Navigation Status

**`mkdocs.yml` line 568:** Already present in navigation:
```yaml
- Configuration Hardening Baseline: playbooks/advanced-implementations/configuration-hardening-baseline/index.md
```

No navigation changes needed.

### 1.3 Governance Scripts Directory

**`scripts/governance/`** contains only a `README.md` with planned scripts. No actual scripts exist yet. The `Invoke-HardeningBaselineCheck.ps1` file will be the first real script in this directory.

---

## 2. Technical Approach

### 2.1 HBL-01: Automation Feasibility Classification

**Approach:** Add an "Automation" column to each of the 6 checklist tables in the hardening baseline document.

#### Classification Logic (from SSPM Alert Mapping)

The `maintainers-local/sspm-alert-mapping.md` "Companion Solution Opportunity" section provides the definitive classification:

| Items | Category | Classification | Rationale |
|-------|----------|---------------|-----------|
| 7–9 | Audit Logging | **Automated** | `Get-AdminPowerAppEnvironment` returns audit settings; tenant-level auditing via PPAC API |
| 14–17 | Environment Provisioning | **Automated** | `Get-TenantSettings` returns creation restrictions; `Get-AdminPowerAppEnvironment` returns security groups; tenant isolation via PPAC API |
| 18–27 | AI Feature Access | **Semi-Automated** | Per-environment feature flags via PPAC API; agent-level toggles require Copilot Studio management API (limited availability) |
| 1–6 | Agent Auth & Access | **Semi-Automated** | Agent-level settings require Copilot Studio management API; tenant-level toggles (items 5–6) accessible via PPAC API or M365 admin API |
| 10 | Content Moderation | **Manual Attestation** | No API access to Copilot Studio content moderation level |
| 11–12 | Action Consent / Connected Agents | **Manual Attestation** | Agent-level settings with no current API |
| 13 | Environment Admin Count | **Semi-Automated** | Dataverse system admin query possible but requires per-environment Dataverse connection |

#### Per-Item Classification (Final)

| # | Setting | Automation |
|---|---------|-----------|
| 1 | Agent authentication mode | Semi-Automated |
| 2 | Require users to sign in | Semi-Automated |
| 3 | Authentication enforcement timing | Semi-Automated |
| 4 | Agent sharing scope | Semi-Automated |
| 5 | Publish bots with AI features | Automated |
| 6 | Unapproved shared agents blocked | Semi-Automated |
| 7 | Environment-level auditing | **Automated** |
| 8 | Audit log retention period | **Automated** |
| 9 | Tenant-level Dataverse auditing | **Automated** |
| 10 | Content moderation level | Manual Attestation |
| 11 | Agent action user consent | Manual Attestation |
| 12 | Connected agent access | Manual Attestation |
| 13 | Environment admin count | Semi-Automated |
| 14 | Environment creation restriction | **Automated** |
| 15 | Environment routing | **Automated** |
| 16 | Tenant isolation | **Automated** |
| 17 | Environment security groups | **Automated** |
| 18 | AI Prompts | Semi-Automated |
| 19 | Generative Actions | Manual Attestation |
| 20 | File Analysis | Manual Attestation |
| 21 | Model Knowledge | Manual Attestation |
| 22 | Semantic Search | Manual Attestation |
| 23 | Generative AI features (per-env) | Semi-Automated |
| 24 | Move Data Across Regions | Semi-Automated |
| 25 | Bing Search | Semi-Automated |
| 26 | Conversational transcript access | Semi-Automated |
| 27 | DLP for agent publishing connectors | Semi-Automated |

**Implementation:** Add `| Automation |` column header and values to all 6 checklist tables in the index.md.

### 2.2 HBL-02: PowerShell Verification Script

**Target file:** `scripts/governance/Invoke-HardeningBaselineCheck.ps1`

#### Scope: Items 7–9 and 14–17 (Automated subset)

These 7 items are fully automatable via existing PowerShell modules:

**Items 7–9: Audit Logging**

| # | Setting | API/Cmdlet | Property Path |
|---|---------|-----------|---------------|
| 7 | Environment-level auditing | `Get-AdminPowerAppEnvironment -EnvironmentName $id` | `Internal.properties.databaseSettings.isAuditEnabled` (Dataverse OData) |
| 8 | Audit log retention period | Dataverse Organization Settings OData query | `Organization.AuditRetentionPeriodV2` |
| 9 | Tenant-level Dataverse auditing | PPAC API or `Get-AdminPowerAppEnvironment` with compliance settings | Tenant-level security compliance settings |

**Items 14–17: Environment Provisioning**

| # | Setting | API/Cmdlet | Property Path |
|---|---------|-----------|---------------|
| 14 | Environment creation restriction | `Get-TenantSettings` | `powerPlatform.environments.disableEnvironmentCreationByNonAdminUsers` or `properties.tenantSettings.powerPlatform.environments.whoCanCreateEnvironments` |
| 15 | Environment routing | `Get-TenantSettings` | `powerPlatform.environments.environmentRouting.isEnabled` |
| 16 | Tenant isolation | PPAC REST API: `GET /providers/Microsoft.BusinessAppPlatform/tenantSettings` | `powerPlatform.tenantIsolation.enabled` |
| 17 | Environment security groups | `Get-AdminPowerAppEnvironment -EnvironmentName $id` | `Properties.securityGroupId` (non-null for Zone 2/3) |

#### Required Modules

```
Microsoft.PowerApps.Administration.PowerShell  (Get-TenantSettings, Get-AdminPowerAppEnvironment)
```

**Note:** Items 7–9 require Dataverse OData API queries rather than pure PowerShell cmdlets. The `Get-AdminPowerAppEnvironment` cmdlet returns environment metadata including linked Dataverse details, but audit settings require Dataverse Organization entity queries. Two approaches:

1. **Preferred (for this script):** Use PPAC Admin API REST calls with `Invoke-RestMethod` against `https://api.bap.microsoft.com` endpoints, consistent with how `Get-TenantSettings` works internally. This avoids additional module dependencies.
2. **Alternative:** Use `Microsoft.Xrm.Data.PowerShell` module with `Get-CrmRecord` queries against each environment's Dataverse Organization table.

**Recommendation:** Use approach 1 (PPAC REST + `Invoke-RestMethod`) for items 7–9 to keep module dependencies minimal. The script already needs `Microsoft.PowerApps.Administration.PowerShell` for items 14–17, so we can reuse its authentication context.

#### Script Architecture (following Test-PolicyCompliance.ps1 patterns)

```
Invoke-HardeningBaselineCheck.ps1
├── Banner + parameters
├── Module/connection validation
├── Check group: Audit Logging (items 7-9)
│   ├── Per-environment audit enablement
│   ├── Per-environment retention period
│   └── Tenant-level auditing
├── Check group: Environment Provisioning (items 14-17)
│   ├── Environment creation restriction
│   ├── Environment routing
│   ├── Tenant isolation
│   └── Per-environment security group
├── Results aggregation
├── Evidence export (JSON + SHA-256 hash)
└── Output (Table / JSON / Object)
```

**Parameters (following existing conventions):**

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `OutputFormat` | `ValidateSet('Table','JSON','Object')` | No (default: Table) | Same pattern as `Test-PolicyCompliance.ps1` |
| `OutputPath` | `string` | No | File path for evidence export |
| `EnvironmentFilter` | `string[]` | No | Specific environment names/GUIDs to check (default: all) |
| `Zone` | `int` (1-3) | No | Filter to specific zone environments |
| `IncludeEvidence` | `switch` | No | Generate SHA-256 hashed evidence package |

**Output Object Structure:**

```json
{
  "metadata": {
    "checkedAt": "2026-02-11T00:00:00Z",
    "checkedBy": "admin@contoso.com",
    "scriptVersion": "1.0.0",
    "environmentsScanned": 5,
    "integrityHash": "A1B2C3..."
  },
  "summary": {
    "totalChecks": 7,
    "passed": 5,
    "failed": 2,
    "overallStatus": "GapsFound"
  },
  "checks": [
    {
      "itemNumber": 7,
      "setting": "Environment-level auditing",
      "category": "Audit Logging",
      "controlRef": "1.7",
      "status": "Passed",
      "environments": [
        { "name": "FSI-Prod", "value": true, "expected": true, "status": "Passed" }
      ]
    }
  ]
}
```

#### API Details for Each Check

**Item 7 — Environment-Level Auditing:**
- **Cmdlet:** `Get-AdminPowerAppEnvironment -EnvironmentName $envId`
- **Fallback:** Dataverse Web API `GET /api/data/v9.2/organizations?$select=isauditenabled`
- **Expected:** `isauditenabled = true`
- **Zone requirement:** All zones

**Item 8 — Audit Log Retention Period:**
- **API:** Dataverse Web API `GET /api/data/v9.2/organizations?$select=auditretentionperiodv2`
- **Expected:** ≥ 180 days (Zone 1), ≥ 365 days (Zone 2), ≥ 730 days (Zone 3)
- **Note:** Requires Dataverse environment URL per environment; obtainable from `Get-AdminPowerAppEnvironment` linked metadata

**Item 9 — Tenant-Level Dataverse Auditing:**
- **API:** PPAC Security & Compliance settings or Dataverse Organization `isauditenabled` at tenant default environment
- **Expected:** Auditing enabled with User Sign-In and Activity checked
- **Note:** This is effectively the default environment's audit config as tenant-level control

**Item 14 — Environment Creation Restriction:**
- **Cmdlet:** `Get-TenantSettings`
- **Property:** `powerPlatform.environments.disableEnvironmentCreationByNonAdminUsers` = `$true`
- **Expected:** Only specific admins can create environments (Dev, Prod, Trial)

**Item 15 — Environment Routing:**
- **Cmdlet:** `Get-TenantSettings`
- **Property:** Look for environment routing configuration
- **Expected:** Configured for correct region

**Item 16 — Tenant Isolation:**
- **Cmdlet:** `Get-TenantSettings` or PPAC REST API
- **Property:** `powerPlatform.tenantIsolation.enabled`
- **Expected:** `$true` (Restrict Cross-Tenant Connections enabled)

**Item 17 — Environment Security Groups:**
- **Cmdlet:** `Get-AdminPowerAppEnvironment -EnvironmentName $envId`
- **Property:** `Properties.securityGroupId` or security group details
- **Expected:** Non-null for Zone 2/3 environments
- **Note:** Zone 1 environments may not require security groups

### 2.3 HBL-03: Evidence Export and Zone-Specific Review Cadence

**Approach:** Add two new sections to the hardening baseline document:

#### Section A: Evidence Export Procedures

Following the pattern established by:
- `docs/playbooks/advanced-implementations/environment-lifecycle-management/evidence-and-audit.md` (lines 260–350)
- `docs/playbooks/advanced-implementations/deny-event-correlation-report/index.md` (SHA-256 evidence export pattern)

**Content to add:**

1. **Evidence Package Format** — JSON structure with metadata (timestamp, reviewer, version, integrity hash), check results, and attestation records
2. **SHA-256 Integrity Hash** — Following the ELM pattern:
   ```powershell
   $jsonForHash = $evidence | ConvertTo-Json -Depth 10
   $hash = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
       [System.Text.Encoding]::UTF8.GetBytes($jsonForHash)
   )
   $evidence.metadata.integrityHash = [BitConverter]::ToString($hash) -replace '-'
   ```
3. **Export procedures** for both automated (script-generated) and manual attestation evidence
4. **Storage recommendations** (SharePoint compliance library, Azure Blob with retention, Dataverse attachment)
5. **Retention alignment** with zone requirements (referencing ELM's retention table)

#### Section B: Zone-Specific Review Cadence Enhancement

Expand the existing Review Frequency table with:

1. **Escalation triggers** — What events force an immediate out-of-cycle review
2. **Review scope per cadence** — Which items to check at each frequency
3. **Evidence archival cadence** — When to export evidence packages
4. **Audit-ready documentation** — What examiners expect to see

---

## 3. Existing Pattern Analysis

### 3.1 Test-PolicyCompliance.ps1 Conventions

From the 443-line script, key patterns to replicate:

| Pattern | Detail | Apply to HBL-02 |
|---------|--------|-----------------|
| **Banner** | ASCII box with solution name | Use "FSI Agent Governance — Hardening Baseline Checker" |
| **#Requires** | Version 7.0, specific modules | `#Requires -Version 7.0`, `#Requires -Modules Microsoft.PowerApps.Administration.PowerShell` |
| **Parameters** | `[CmdletBinding(SupportsShouldProcess)]`, Mandatory/Optional grouping | Same pattern |
| **Private helper imports** | `. "$PSScriptRoot/private/filename.ps1"` | Not needed — self-contained script for v1 |
| **Check numbering** | `# ─── Check 1: Description ───` with ASCII decoration | Reuse for check groups |
| **Results object** | `$complianceResults` PSCustomObject with Checks, Gaps, Summary | Adapt to `$baselineResults` |
| **Output switch** | Table/JSON/Object with `$OutputPath` export | Same pattern |
| **Gap tracking** | `$complianceResults.Gaps += "message"` | Same pattern |
| **Summary display** | Colored console output with pass/fail counts | Same pattern |
| **Evidence export** | JSON with `ConvertTo-Json -Depth 10`, `Out-File -Encoding utf8` | Add SHA-256 hash |

### 3.2 SHA-256 Hash Pattern

From `scripts/private/Get-PolicyBaseline.ps1`:

```powershell
$configString = ($policy | ConvertTo-Json -Depth 20 -Compress)
$hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
    [System.Text.Encoding]::UTF8.GetBytes($configString)
)
$configHash = [BitConverter]::ToString($hashBytes) -replace '-'
```

From ELM `evidence-and-audit.md`:

```powershell
$jsonForHash = $evidence | ConvertTo-Json -Depth 10
$hash = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
    [System.Text.Encoding]::UTF8.GetBytes($jsonForHash)
)
$evidence.metadata.integrityHash = [BitConverter]::ToString($hash) -replace '-'
```

Both patterns are consistent. Use `-Depth 10` for evidence packages (matching ELM) and `-Compress` for config hashes (matching CAA baseline).

### 3.3 Connect-GraphSession Pattern

The `Connect-CAAGraphSession` pattern wraps `Connect-MgGraph` with scope validation. For the hardening baseline script, we do **not** need Graph API — all checks use Power Platform Admin PowerShell (`Get-TenantSettings`, `Get-AdminPowerAppEnvironment`). Graph is only needed for Microsoft 365 admin settings (items 5–6) which are classified as Semi-Automated and outside this script's scope.

**Authentication pattern for this script:**
```powershell
# Interactive
Add-PowerAppsAccount

# Service principal (for automation scenarios)
Add-PowerAppsAccount -ApplicationId $AppId -ClientSecret $Secret -TenantID $TenantId
```

### 3.4 Zone Classification Pattern

From `Get-CAAZoneClassification`:
- Derives zone from display name prefix convention
- FSI naming: `FSI-Z{n}` prefix
- Returns integer 1/2/3 or 0 for unknown

For the hardening baseline script, zone classification is needed for:
- Item 8 (retention thresholds vary by zone)
- Item 17 (security groups required for Zone 2/3 only)
- Evidence export (zone-tagged results)

**Approach:** Accept `-Zone` parameter or derive from environment metadata. Environments don't natively have zone classification — this requires an external mapping (e.g., environment name convention, Dataverse lookup, or parameter input).

**Recommendation:** Accept a `-ZoneMapping` parameter (hashtable or JSON file) that maps environment GUIDs to zones. If not provided, treat all environments as Zone 1 (minimum requirements).

---

## 4. API/Cmdlet Research

### 4.1 Power Platform Admin PowerShell Module

**Module:** `Microsoft.PowerApps.Administration.PowerShell`
**Install:** `Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -Scope CurrentUser`

**Key cmdlets for this script:**

| Cmdlet | Purpose | Items |
|--------|---------|-------|
| `Get-TenantSettings` | Returns tenant-wide Power Platform configuration | 14, 15, 16 |
| `Get-AdminPowerAppEnvironment` | Returns environment metadata including security groups | 7, 8, 17 |
| `Get-AdminPowerAppEnvironment -EnvironmentName $id` | Returns specific environment details | 7, 8, 17 |
| `Add-PowerAppsAccount` | Authentication (interactive or service principal) | N/A |

**Tenant Settings Object Structure (relevant paths):**

```
$settings.powerPlatform.environments
  .disableEnvironmentCreationByNonAdminUsers  → Item 14
  
$settings.powerPlatform.tenantIsolation
  .enabled                                    → Item 16
  
$settings.powerPlatform.environments  
  (environment routing settings)              → Item 15
```

### 4.2 Dataverse Web API (for Audit Settings)

Items 7–9 require Dataverse Organization entity queries:

**Approach:** For each environment with a linked Dataverse instance, query the Organization entity:

```
GET {environmentUrl}/api/data/v9.2/organizations?$select=isauditenabled,auditretentionperiodv2
```

**Authentication:** Reuse the Power Platform admin token or acquire per-environment Dataverse tokens.

**Practical consideration:** The `Get-AdminPowerAppEnvironment` response includes `Properties.linkedEnvironmentMetadata.instanceUrl` which gives the Dataverse URL for each environment. We can iterate environments and query each Dataverse instance.

**Fallback:** For environments without Dataverse, items 7–9 are N/A (audit logging requires Dataverse).

### 4.3 Module Dependencies Summary

| Module | Required For | Already Used In Repo |
|--------|-------------|---------------------|
| `Microsoft.PowerApps.Administration.PowerShell` | Items 14–17 + env listing | Yes (2.1 playbook, 1.1 playbook) |
| None additional required | Items 7–9 use REST API with existing auth | — |

**Not required:**
- `Microsoft.Graph.*` — Not needed for these specific checks
- `Microsoft.Xrm.Data.PowerShell` — Avoided by using REST API

---

## 5. Risks and Dependencies

### 5.1 Technical Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Dataverse audit settings require per-environment API calls** | Medium | Rate-limit requests; parallelize with `-ThrottleLimit`; cache results |
| **Environment Dataverse URL may not be accessible** | Medium | Graceful skip with warning for environments without Dataverse |
| **Tenant isolation API may move to different endpoint** | Low | Use `Get-TenantSettings` which is stable and well-documented |
| **Zone mapping requires external input** | Medium | Provide sensible defaults (Zone 1 minimum thresholds) when `-ZoneMapping` not specified |
| **Service principal auth may lack Dataverse permissions** | Medium | Document required permissions in script header; fall back to interactive auth |

### 5.2 Scope Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Items 7–9 audit check depth** | Medium | v1 checks enablement and retention only; detailed audit category checks deferred to future version |
| **Environment routing verification** | Low | `Get-TenantSettings` returns routing config but "correct region" is subjective — report value, let admin assess |
| **Large tenant with many environments** | Medium | Environment filter parameter allows scoping; progress output for large scans |

### 5.3 Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Hardening baseline doc exists | ✅ Complete | 27-item checklist in place |
| `scripts/governance/` directory exists | ✅ Exists | Has README.md only |
| PowerShell coding patterns established | ✅ Available | `Test-PolicyCompliance.ps1` provides template |
| SHA-256 evidence pattern documented | ✅ Available | ELM and CAA both use it |
| mkdocs.yml nav entry exists | ✅ Present | Line 568 |
| Zone mapping convention defined | ⚠️ Not standardized | Need to define approach for environment-to-zone mapping |

---

## 6. Recommended Task Breakdown

### Task 1: Update Hardening Baseline Checklist with Automation Column (HBL-01)

**File:** `docs/playbooks/advanced-implementations/configuration-hardening-baseline/index.md`
**Effort:** Small (content update — add column to 6 tables)

**Changes:**
1. Add `| Automation |` column to all 6 checklist tables
2. Populate each row with: `Automated`, `Semi-Automated`, or `Manual Attestation`
3. Add a legend/key explaining the three classification levels immediately before or after the checklist
4. Update the "Integration with Existing Solutions" section to reference the new script

### Task 2: Create PowerShell Verification Script (HBL-02)

**File:** `scripts/governance/Invoke-HardeningBaselineCheck.ps1`
**Effort:** Medium (new script ~250–350 lines)

**Structure:**
1. Script header (synopsis, description, parameters, examples, notes)
2. `#Requires` statements
3. Parameter block (`OutputFormat`, `OutputPath`, `EnvironmentFilter`, `Zone`, `IncludeEvidence`)
4. Banner display
5. Authentication (`Add-PowerAppsAccount`)
6. Environment discovery (`Get-AdminPowerAppEnvironment`)
7. Check Group A: Audit Logging (items 7–9)
   - Per-environment audit enablement via Dataverse API
   - Per-environment retention period via Dataverse API
   - Tenant-level auditing via default environment check
8. Check Group B: Environment Provisioning (items 14–17)
   - `Get-TenantSettings` for items 14, 15, 16
   - Per-environment security group check for item 17
9. Results aggregation and summary
10. Evidence export with SHA-256 hash (when `-IncludeEvidence` specified)
11. Output formatting (Table/JSON/Object)

### Task 3: Add Evidence Export and Cadence Guidance (HBL-03)

**File:** `docs/playbooks/advanced-implementations/configuration-hardening-baseline/index.md`
**Effort:** Medium (new sections ~100–150 lines of documentation)

**New sections to add (before "Related Resources"):**

1. **Evidence Export Procedures**
   - Evidence package JSON format specification
   - SHA-256 integrity hash procedure (PowerShell code block)
   - Automated evidence via `Invoke-HardeningBaselineCheck.ps1 -IncludeEvidence`
   - Manual attestation evidence compilation
   - Storage recommendations (SharePoint, Azure Blob, Dataverse)

2. **Zone-Specific Review Cadence Guidance**
   - Expand existing Review Frequency table
   - Add escalation triggers (setting drift, regulatory change, security incident)
   - Add review scope matrix (which items at which frequency)
   - Add evidence archival schedule
   - Add audit-readiness documentation guidance

3. **Examiner Readiness**
   - What to present during regulatory examination
   - How to demonstrate configuration posture
   - Cross-reference to evidence packages

### Task 4: Update Governance Scripts README (Housekeeping)

**File:** `scripts/governance/README.md`
**Effort:** Small

**Changes:**
- Add `Invoke-HardeningBaselineCheck.ps1` to the scripts table
- Update prerequisites if needed
- Add usage examples

### Execution Order

```
Task 1 (HBL-01) → can start immediately, no dependencies
Task 2 (HBL-02) → can start immediately, parallel with Task 1
Task 3 (HBL-03) → after Task 2 (references script output format)
Task 4 (README)  → after Task 2 (references script name)
```

**Recommended wave structure:**
- **Wave 1:** Task 1 + Task 2 (parallel)
- **Wave 2:** Task 3 + Task 4 (parallel, after Wave 1)

---

## 7. Validation Plan

After all tasks complete:

1. `mkdocs build --strict` — Validate site builds (hardening baseline doc changes)
2. `pwsh -c "Get-Help ./scripts/governance/Invoke-HardeningBaselineCheck.ps1"` — Verify script help
3. `pwsh -c "./scripts/governance/Invoke-HardeningBaselineCheck.ps1 -WhatIf"` — Syntax validation (if ShouldProcess supported)
4. Manual review: Verify all 27 items have automation classification
5. Manual review: Verify evidence export section includes SHA-256 hash code block
6. Manual review: Verify zone-specific cadence guidance has escalation triggers

---

## 8. Reference File Index

| File | Purpose in This Phase |
|------|----------------------|
| `docs/playbooks/advanced-implementations/configuration-hardening-baseline/index.md` | **Primary target** — update checklist, add evidence/cadence sections |
| `scripts/governance/Invoke-HardeningBaselineCheck.ps1` | **New file** — PowerShell verification script |
| `scripts/governance/README.md` | **Update** — add script reference |
| `scripts/Test-PolicyCompliance.ps1` | **Reference** — coding conventions, output format, banner style |
| `scripts/private/Get-PolicyBaseline.ps1` | **Reference** — SHA-256 hash pattern |
| `scripts/private/Connect-GraphSession.ps1` | **Reference** — authentication wrapper pattern |
| `scripts/private/Get-ZoneClassification.ps1` | **Reference** — zone derivation pattern |
| `scripts/Start-CAAValidationRunbook.ps1` | **Reference** — runbook pattern, evidence export, error handling |
| `docs/playbooks/advanced-implementations/environment-lifecycle-management/evidence-and-audit.md` | **Reference** — SHA-256 evidence package pattern, quarterly export procedure |
| `docs/playbooks/advanced-implementations/deny-event-correlation-report/index.md` | **Reference** — SHA-256 hashed evidence package references |
| `maintainers-local/sspm-alert-mapping.md` | **Reference** — automation feasibility classification source |
| `docs/playbooks/control-implementations/1.1/powershell-setup.md` | **Reference** — `Get-TenantSettings` / `Set-TenantSettings` usage |
| `docs/playbooks/control-implementations/2.1/powershell-setup.md` | **Reference** — `Get-AdminPowerAppEnvironment` usage patterns |
