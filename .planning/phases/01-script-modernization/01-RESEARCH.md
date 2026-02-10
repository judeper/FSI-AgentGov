# Phase 1 Research: Script Modernization & Core Validation

**Phase:** 01 - Script Modernization & Core Validation  
**Date:** 2026-02-10  
**Status:** Complete  

---

## 1. Current State Analysis — Existing CA Scripts

### 1.1 Deploy-CAPolicies.ps1

| Attribute | Value |
|-----------|-------|
| **Line count** | 226 lines |
| **Functions defined** | 0 (monolithic script) |
| **#Requires** | `-Version 7.0`, `-Modules Microsoft.Graph.Identity.SignIns` |
| **Parameter sets** | Single set: `TenantId` (M), `ConfigPath` (M), `TemplateSet`, `TemplatePath`, `EnablePolicies`, `DryRun`, `Force` |
| **Error handling** | `$ErrorActionPreference = "Stop"`, try/catch per policy, collects `$errors` array |
| **Dry-run support** | Yes (`-DryRun` switch) — previews policies without Graph calls |
| **Module dependencies** | `Microsoft.Graph.Identity.SignIns` |

**Strengths:**
- Already has `-DryRun` switch (SMC-04 partially met)
- Template substitution logic is clean (group IDs, break-glass, app IDs)
- Zone-to-template mapping is hardcoded but correct
- Report-only default deployment (safe)
- `-Force` flag for update-vs-skip behavior

**Gaps vs Tier 2:**
- No module structure — standalone script, not importable
- No `-WhatIf` / `SupportsShouldProcess` (uses custom `-DryRun` instead)
- No private helper functions
- No zone lookup integration (ELM / naming convention)
- No policy drift detection (just deployment)
- Hardcoded template mapping (not configurable)
- No `Write-Verbose` / structured logging (uses `Write-Host` only)
- No `.psd1` manifest

### 1.2 Register-ServicePrincipal.ps1

| Attribute | Value |
|-----------|-------|
| **Line count** | 157 lines |
| **Functions defined** | 0 (monolithic script) |
| **#Requires** | `-Version 7.0`, `-Modules Microsoft.Graph.Applications, Az.KeyVault` |
| **Parameter sets** | Single set: `TenantId` (M), `AppName` (M), `KeyVaultName` (M), `DryRun` |
| **Error handling** | `$ErrorActionPreference = "Stop"`, try/catch for Key Vault only |
| **Dry-run support** | Yes (`-DryRun` switch) |
| **Module dependencies** | `Microsoft.Graph.Applications`, `Az.KeyVault` |

**Strengths:**
- Has `-DryRun` switch
- Graceful Key Vault fallback (shows credentials if vault inaccessible)
- Admin consent URL generation
- Interactive confirmation for existing app updates

**Gaps vs Tier 2:**
- No module structure
- No `SupportsShouldProcess`
- Uses `Read-Host` for interactive confirmation (not pipeline-safe)
- Hardcoded permission GUIDs (not documented inline)
- No private helper functions

### 1.3 Test-PolicyCompliance.ps1

| Attribute | Value |
|-----------|-------|
| **Line count** | 291 lines |
| **Functions defined** | 0 (monolithic script) |
| **#Requires** | `-Version 7.0`, `-Modules Microsoft.Graph.Identity.SignIns` |
| **Parameter sets** | Single set: `TenantId` (M), `ConfigPath` (M), `OutputPath` (M), `IncludeReportOnly` |
| **Error handling** | `$ErrorActionPreference = "Stop"`, per-section try/catch, structured error output |
| **Dry-run support** | **No** (always live queries) |
| **Module dependencies** | `Microsoft.Graph.Identity.SignIns` |

**Strengths:**
- 4 compliance checks: existence, state, break-glass exclusions, MFA
- Zone coverage tracking
- Structured JSON output to files
- Compliance rate calculation with thresholds (95%/80%)
- Gap identification with recommendations

**Gaps vs Tier 2:**
- No dry-run mode (SMC-04)
- No module structure
- No drift detection (compares against expected patterns, not baseline snapshots)
- No zone lookup integration
- No `SupportsShouldProcess`
- Hardcoded expected policy patterns
- No session control validation (only grant controls)
- No Dataverse persistence

---

## 2. Policy Template Schema Analysis

### 2.1 Template Inventory

| Template File | Zone | Lines | Unique Properties |
|--------------|------|-------|-------------------|
| CA-CopilotStudio-Zone1.json | Zone 1 | 24 | `signInRiskLevels` |
| CA-CopilotStudio-Zone2.json | Zone 2 | 21 | — |
| CA-CopilotStudio-Zone3.json | Zone 3 | 27 | `persistentBrowser`, AND operator |
| CA-AgentBuilder-Zone2.json | Zone 2 | 21 | — |
| CA-AgentBuilder-Zone3.json | Zone 3 | 27 | `persistentBrowser`, AND operator |
| CA-M365Copilot-AllZones.json | All | 24 | `excludeGuestsOrExternalUsers`, hardcoded app ID |
| CA-BlockLegacyAuth-AI.json | All | 17 | `block` grant, legacy `clientAppTypes` |
| CA-RequireCompliantDevice-Zone3.json | Zone 3 | 21 | `platforms`, `domainJoinedDevice` |

### 2.2 Common Schema Structure

All templates follow this Graph API `conditionalAccessPolicy` resource schema:

```
{
  displayName: string
  state: "enabledForReportingButNotEnforced"
  conditions: {
    users: {
      includeGroups?: string[]      // Zone-specific group
      includeUsers?: string[]       // "All" for cross-zone
      excludeUsers: string[]        // Break-glass accounts
      excludeGuestsOrExternalUsers?: object  // M365 Copilot only
    }
    applications: {
      includeApplications: string[] // App IDs (placeholder or hardcoded)
    }
    signInRiskLevels?: string[]     // Zone 1 only
    clientAppTypes: string[]        // "browser", "mobileAppsAndDesktopClients", or legacy
    platforms?: {                   // Device compliance only
      includePlatforms: string[]
    }
  }
  grantControls: {
    operator: "OR" | "AND"
    builtInControls: string[]       // "mfa", "compliantDevice", "domainJoinedDevice", "block"
  }
  sessionControls?: {
    signInFrequency?: {
      value: number
      type: "hours"
      isEnabled: boolean
    }
    persistentBrowser?: {
      mode: "never"
      isEnabled: boolean
    }
  }
}
```

### 2.3 Graph API Property Analysis

**Properties used (current templates vs Graph API v1.0):**

| Property | Used | Graph API Status |
|----------|------|-----------------|
| `displayName` | ✓ | Current |
| `state` | ✓ | Current |
| `conditions.users.includeGroups` | ✓ | Current |
| `conditions.users.includeUsers` | ✓ | Current |
| `conditions.users.excludeUsers` | ✓ | Current |
| `conditions.users.excludeGuestsOrExternalUsers` | ✓ | Current (v1.0) |
| `conditions.applications.includeApplications` | ✓ | Current |
| `conditions.signInRiskLevels` | ✓ | Current (requires P2) |
| `conditions.clientAppTypes` | ✓ | Current |
| `conditions.platforms.includePlatforms` | ✓ | Current |
| `grantControls.operator` | ✓ | Current |
| `grantControls.builtInControls` | ✓ | Current |
| `sessionControls.signInFrequency` | ✓ | Current |
| `sessionControls.persistentBrowser` | ✓ | Current |

**Potentially missing Graph API properties to consider:**
- `grantControls.authenticationStrength` — Used by SSC Zone 2/3 baselines, not in CA templates
- `conditions.userRiskLevels` — Referenced in Zone3 template docs but empty array
- `conditions.locations` — Not used (could add location-based controls)
- `conditions.devices.deviceFilter` — Alternative to `platforms` for device targeting
- `grantControls.termsOfUse` — FSI compliance could benefit

**No deprecated properties detected.** All properties used are current Graph API v1.0.

### 2.4 Break-Glass Exclusion Patterns

All 8 templates use `excludeUsers` with placeholder values `<break-glass-1>` and `<break-glass-2>`. The deployment script substitutes from `config.breakGlassAccounts` array. This is correct and consistent.

### 2.5 Placeholder Tokens

| Token | Used In | Config Key |
|-------|---------|------------|
| `<zone-1-users-group-id>` | Zone 1 templates | `config.groups.zone1Users` |
| `<zone-2-users-group-id>` | Zone 2 templates | `config.groups.zone2Users` |
| `<zone-3-users-group-id>` | Zone 3 templates | `config.groups.zone3Users` |
| `<break-glass-1>`, `<break-glass-2>` | All templates | `config.breakGlassAccounts` |
| `<copilot-studio-app-id>` | Copilot Studio templates | `config.applications.copilotStudio` |
| `<agent-builder-app-id>` | Agent Builder templates | `config.applications.agentBuilder` |
| `<m365-copilot-app-id>` | M365 template | `config.applications.m365Copilot` |
| `fb8d773d-7ef8-4ec0-a117-179f88add510` | M365 Copilot, BlockLegacy | **Hardcoded** (M365 Copilot well-known ID) |

**Issue:** M365 Copilot app ID is both hardcoded and placeholder-based across templates. The BlockLegacyAuth and M365Copilot templates use the hardcoded ID, but Deploy-CAPolicies only substitutes `<m365-copilot-app-id>`. This inconsistency should be normalized.

---

## 3. Tier 2 Module Pattern Summary

### 3.1 Pattern Sources Analyzed

| Solution | Module Type | Key Files |
|----------|-------------|-----------|
| **AAM** (Agent Access Monitor) | PowerShell `.psd1` + `.psm1` | `agent-access-monitor.psd1`, `private/AAMClient.psm1`, 4 private scripts, 3 public scripts |
| **ACV** (Audit Configuration Validator) | Python `acv_client.py` | `acv_client.py`, 6 private PS scripts |
| **SSC** (Session Security Configurator) | Python `ssc_client.py` | `ssc_client.py`, 5 private PS scripts |

### 3.2 Canonical Tier 2 Module Structure

Based on AAM (the most complete PowerShell module pattern):

```
solution-name/
├── scripts/
│   ├── solution-name.psd1           # Module manifest (exports, metadata, dependencies)
│   ├── xxx_client.py                # Dataverse Web API client (Python)
│   ├── Public-Script-1.ps1          # Public entry point (orchestrator)
│   ├── Public-Script-2.ps1          # Public entry point (settings query)
│   ├── Public-Script-3.ps1          # Public entry point (comparison)
│   ├── Export-Evidence.ps1           # Evidence export script
│   ├── private/
│   │   ├── XXXClient.psm1           # Dataverse integration module
│   │   ├── Connect-GraphSession.ps1  # Authentication helper
│   │   ├── Get-ZoneClassification.ps1 # Zone lookup (ELM + fallback)
│   │   ├── Get-ExpectedSettings.ps1  # Baseline loading
│   │   ├── Test-ParameterValidation.ps1 # Input validation helpers
│   │   └── Compare-Baseline.ps1      # Drift detection
│   ├── create_dataverse_schema.py    # Schema deployment
│   ├── create_environment_variables.py # Env var setup
│   ├── create_connection_references.py # Connection ref setup
│   ├── deploy.py                     # Orchestrated deployment
│   └── requirements.txt
├── templates/
│   └── zone-settings-baseline.json   # Zone baseline definitions
├── src/
│   └── (Power Automate flow JSON, Adaptive Cards)
├── docs/
│   └── (solution documentation)
├── CHANGELOG.md
└── README.md
```

### 3.3 Key Tier 2 Conventions

| Convention | Pattern | Source |
|------------|---------|-------|
| **Module manifest** | `.psd1` with `FunctionsToExport`, `RequiredModules`, `CompatiblePSEditions = @('Core')` | AAM |
| **Private module** | `private/XXXClient.psm1` — Dataverse CRUD, connection management, module-scoped variables | AAM, SSC |
| **Zone lookup** | `private/Get-ZoneClassification.ps1` — ELM Dataverse first, naming convention fallback | AAM |
| **Parameter validation** | `private/Test-ParameterValidation.ps1` — reusable validation functions | AAM |
| **SupportsShouldProcess** | `[CmdletBinding(SupportsShouldProcess)]` on orchestrators | AAM |
| **Dry-run** | `-WhatIf` via `SupportsShouldProcess` (not custom `-DryRun`) | AAM |
| **Error handling** | `$ErrorActionPreference = "Stop"`, try/catch, `Write-Warning` for non-fatal | All |
| **Verbose logging** | `Write-Verbose` for operational messages, `Write-Host` only for banner/summary | AAM, SSC |
| **Output formats** | `-OutputFormat Table|JSON|Object` parameter | AAM |
| **#Requires** | At script-level, specifying `-Version 7.0` and `-Modules` | All |
| **Help comments** | Full `.SYNOPSIS`, `.DESCRIPTION`, `.PARAMETER`, `.EXAMPLE`, `.OUTPUTS`, `.NOTES` | All |
| **Evidence export** | Dedicated `Export-*Evidence.ps1` with SHA-256 hashing and manifest | AAM, ACV |
| **Baseline comparison** | `Compare-*Baseline.ps1` — drift = current severity > baseline severity | ACV, SSC |

### 3.4 Module Manifest Pattern (from AAM .psd1)

```powershell
@{
    ModuleVersion        = '0.1.0'
    CompatiblePSEditions = @('Core')
    GUID                 = '<unique-guid>'
    Author               = 'FSI Agent Governance Framework'
    CompanyName          = 'Microsoft'
    Copyright            = '(c) 2026 FSI Agent Governance Framework. MIT License.'
    Description          = '<solution description>'
    PowerShellVersion    = '7.0'
    RequiredModules      = @(
        @{ ModuleName = 'Microsoft.Graph.Identity.SignIns'; ModuleVersion = '2.0.0' }
    )
    FunctionsToExport    = @('Public-Function-1', 'Public-Function-2')
    CmdletsToExport      = @()
    VariablesToExport    = @()
    AliasesToExport      = @()
    PrivateData          = @{
        PSData = @{
            Tags = @('ConditionalAccess', 'Governance', 'FSI', ...)
            ReleaseNotes = '...'
        }
    }
}
```

### 3.5 AAMClient.psm1 Function Exports (Pattern)

```
Connect-AAMDataverse       # Establish Dataverse connection
Get-AAMConnection          # Get connection info
Get-AAMEnvironmentVariable # Read env vars from Dataverse
Get-AAMActiveBaseline      # Retrieve active baseline
Write-AAMValidationHistory # Write immutable validation record
Write-AAMViolation         # Write violation record
Save-AAMBaseline           # Save new baseline (deactivate old)
Get-AAMLastValidation      # Query recent validation history
```

---

## 4. Zone Lookup Pattern

### 4.1 Canonical Implementation (from AAM Get-ZoneClassification.ps1)

**Two-layer lookup with graceful fallback:**

1. **ELM Dataverse lookup** (primary, when DataverseUrl provided):
   - Query `fsi_environments` table filtered by `fsi_environment_guid`
   - Read `fsi_zone_classification` option set value
   - Map option set values: `100000000 → Zone1`, `100000001 → Zone2`, `100000002 → Zone3`

2. **Naming convention fallback** (when ELM unavailable or env not found):
   - Pattern matching on display name (case-insensitive)
   - Zone3 patterns: `-z3-`, `-zone3-`, `_zone3_`, `-prod-`, `-enterprise-`
   - Zone2 patterns: `-z2-`, `-zone2-`, `_zone2_`, `-team-`, `-collab-`, `-shared-`
   - Zone1 patterns: `-z1-`, `-zone1-`, `_zone1_`, `-personal-`, `-dev-`, `-sandbox-`
   - Also checks end-of-string: `z3$`, `zone3$`, etc.

3. **Returns `'Unknown'`** if neither method resolves

### 4.2 Integration Point for CAAClient

The CA solution needs zone lookup for:
- **Policy deployment:** Select templates based on target environment zone
- **Compliance testing:** Determine expected policy coverage per zone
- **Drift detection:** Compare deployed policies against zone-specific baselines

The CA solution operates at the **Entra ID tenant level** (not Power Platform environment level), so zone lookup maps **security groups to zones** rather than environments to zones. This is a key difference from AAM.

**Adaptation needed:** CAAClient zone lookup will:
1. Query ELM for environment-to-zone mapping (same as AAM)
2. Map zones to security group assignments
3. Fall back to naming convention on group display names

---

## 5. Documentation State (Current CA Docs)

| File | Lines | Content | Quality |
|------|-------|---------|---------|
| `deployment-guide.md` | ~450 | Full 7-step deployment workflow with commands | Good — complete, actionable |
| `prerequisites.md` | ~290 | Licensing, roles, Key Vault, PowerShell, network, break-glass | Good — comprehensive |
| `policy-templates.md` | ~414 | Template specifications, per-template breakdowns | Good — matches templates |
| `compliance-monitoring.md` | ~403 | Monitoring overview, drift detection, evidence export | Good — references unwritten scripts |
| `troubleshooting.md` | ~421 | Common issues and resolution procedures | Good — practical |

**Key documentation gaps:**
- Docs reference scripts that don't exist yet: `Watch-PolicyDrift.ps1`, `Export-PolicyEvidence.ps1`, `Export-PolicyBaseline.ps1`, `Test-Prerequisites.ps1`, `Test-Configuration.ps1`
- No module import / installation docs (since no module exists yet)
- No architecture diagram showing how CAAClient module fits
- Zone lookup integration not documented

---

## 6. Risk Assessment

### High Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Graph API breaking changes** | Templates could become invalid | Validate templates against Graph API schema before deployment; add schema version to templates |
| **Existing script consumers** | Changing parameters breaks existing callers | Maintain backward-compatible parameter aliases |

### Medium Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| **M365 Copilot app ID changes** | Hardcoded ID becomes stale | Move to config-only substitution; warn if well-known ID changes |
| **Zone group mapping complexity** | CA targets groups, not environments | Design clear group-to-zone mapping in config; document relationship |
| **Module load path issues** | `Import-Module` path resolution across environments | Use `$PSScriptRoot`-relative paths consistently |

### Low Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| **PowerShell 7.0 minimum** | Already established across all solutions | No change needed |
| **Microsoft.Graph module version** | Already required | Pin minimum version in `.psd1` |

---

## 7. Recommended Approach for Phase 1

### 7.1 Target CAAClient Module Structure

```
conditional-access-automation/
├── scripts/
│   ├── conditional-access-automation.psd1  # Module manifest
│   ├── caa_client.py                       # Dataverse Web API client (Python)
│   ├── Deploy-CAPolicies.ps1               # Refactored: uses private helpers
│   ├── Register-ServicePrincipal.ps1       # Minor refactor: SupportsShouldProcess
│   ├── Test-PolicyCompliance.ps1           # Major refactor: modularized checks
│   ├── Watch-PolicyDrift.ps1               # NEW: drift detection
│   ├── Export-PolicyEvidence.ps1           # NEW: evidence export stub
│   ├── Export-PolicyBaseline.ps1           # NEW: baseline capture
│   ├── private/
│   │   ├── CAAClient.psm1                 # Dataverse integration module
│   │   ├── Connect-GraphSession.ps1       # Auth helper (from SSC pattern)
│   │   ├── Get-ZoneClassification.ps1     # Zone lookup (from AAM pattern)
│   │   ├── Get-PolicyBaseline.ps1         # Load/compare policy baselines
│   │   ├── Test-ParameterValidation.ps1   # Input validation helpers
│   │   └── Compare-PolicyBaseline.ps1     # Drift detection logic
│   ├── create_dataverse_schema.py          # Schema deployment
│   ├── create_environment_variables.py     # Env var setup
│   ├── create_connection_references.py     # Connection ref setup
│   ├── deploy.py                           # Orchestrated deployment
│   └── requirements.txt
├── templates/
│   ├── CA-CopilotStudio-Zone1.json         # Existing (validated)
│   ├── CA-CopilotStudio-Zone2.json         # Existing (validated)
│   ├── CA-CopilotStudio-Zone3.json         # Existing (validated)
│   ├── CA-AgentBuilder-Zone2.json          # Existing (validated)
│   ├── CA-AgentBuilder-Zone3.json          # Existing (validated)
│   ├── CA-M365Copilot-AllZones.json        # Existing (fix hardcoded ID)
│   ├── CA-BlockLegacyAuth-AI.json          # Existing (validated)
│   └── CA-RequireCompliantDevice-Zone3.json # Existing (validated)
├── src/
│   └── (Power Automate flows — Phase 2)
├── docs/
│   ├── deployment-guide.md                 # Update for module
│   ├── prerequisites.md                    # Update for module
│   ├── policy-templates.md                 # Update schema section
│   ├── compliance-monitoring.md            # Update for new scripts
│   └── troubleshooting.md                  # Update for module
├── CHANGELOG.md
└── README.md
```

### 7.2 File Manifest — What to Create / Modify

#### New Files (Phase 1 Scope)

| File | Purpose | Complexity | Req |
|------|---------|-----------|-----|
| `scripts/conditional-access-automation.psd1` | Module manifest | Low | SMC-01 |
| `scripts/private/CAAClient.psm1` | Dataverse client module | Medium | SMC-01 |
| `scripts/private/Connect-GraphSession.ps1` | Graph auth helper | Low (adapt SSC) | SMC-01 |
| `scripts/private/Get-ZoneClassification.ps1` | Zone lookup | Low (adapt AAM) | SMC-03 |
| `scripts/private/Test-ParameterValidation.ps1` | Validation helpers | Low (adapt AAM) | SMC-01 |
| `scripts/private/Compare-PolicyBaseline.ps1` | Drift detection logic | High | SMC-05 |
| `scripts/private/Get-PolicyBaseline.ps1` | Baseline loading/snapshot | Medium | SMC-05 |
| `scripts/Watch-PolicyDrift.ps1` | Drift detection orchestrator | High | SMC-05 |
| `scripts/Export-PolicyBaseline.ps1` | Baseline export | Medium | SMC-05 |
| `scripts/caa_client.py` | Python Dataverse client | Low (adapt ACV) | SMC-01 |
| `scripts/create_dataverse_schema.py` | Schema deployment | Medium | SMC-01 |
| `scripts/create_environment_variables.py` | Env var setup | Low | SMC-01 |
| `scripts/create_connection_references.py` | Connection refs | Low | SMC-01 |
| `scripts/deploy.py` | Python deployment orchestrator | Low | SMC-01 |
| `scripts/requirements.txt` | Python dependencies | Low | SMC-01 |

#### Existing Files to Modify

| File | Changes | Complexity | Req |
|------|---------|-----------|-----|
| `scripts/Deploy-CAPolicies.ps1` | Add `SupportsShouldProcess`, private helper imports, zone lookup, verbose logging | Medium | SMC-01, SMC-03, SMC-04 |
| `scripts/Register-ServicePrincipal.ps1` | Add `SupportsShouldProcess`, replace `Read-Host` | Low | SMC-04 |
| `scripts/Test-PolicyCompliance.ps1` | Modularize checks into privates, add dry-run, session control checks, zone lookup | High | SMC-01, SMC-03, SMC-04 |
| Templates (8 files) | Validate against Graph API, normalize M365 Copilot ID | Low | SMC-02 |

### 7.3 Estimated Complexity Per Requirement

| Requirement | Description | Estimated Effort | Files Affected |
|------------|-------------|------------------|----------------|
| **SMC-01** | CAAClient module structure | **Medium** (3-4 days) | ~15 new files, 3 refactored scripts |
| **SMC-02** | Validate 8 policy templates | **Low** (0.5 day) | 8 template JSONs, 1 validation script |
| **SMC-03** | Zone lookup integration | **Low** (0.5 day) | 1 new file (adapt AAM), integrate into 2 scripts |
| **SMC-04** | Dry-run mode for all ops | **Low** (0.5 day) | 3 existing scripts (add SupportsShouldProcess) |
| **SMC-05** | Policy drift detection | **High** (3-4 days) | 3 new files, 1 existing refactor |

**Total estimated effort:** 8-10 working days

### 7.4 Implementation Order

1. **Wave 1 — Foundation (SMC-01 core)**
   - Create `.psd1` manifest
   - Create `private/` directory with helper scripts (adapt from AAM/SSC)
   - Create `CAAClient.psm1` (adapt from AAM pattern)
   - Create Python Dataverse client and deployment scripts

2. **Wave 2 — Template Validation (SMC-02)**
   - Validate all 8 templates against Graph API schema
   - Fix M365 Copilot hardcoded ID inconsistency
   - Add schema version metadata to templates

3. **Wave 3 — Zone Lookup + Dry-Run (SMC-03, SMC-04)**
   - Adapt `Get-ZoneClassification.ps1` from AAM
   - Add `SupportsShouldProcess` to all 3 existing scripts
   - Integrate zone lookup into Deploy and Test scripts

4. **Wave 4 — Drift Detection (SMC-05)**
   - Create `Compare-PolicyBaseline.ps1` (adapt from ACV)
   - Create `Export-PolicyBaseline.ps1`
   - Create `Watch-PolicyDrift.ps1` orchestrator
   - Integrate drift detection into Test-PolicyCompliance

---

## 8. Key Design Decisions

### 8.1 Module Name: `conditional-access-automation`
- Follows AAM pattern: `agent-access-monitor.psd1`
- Exports: `Deploy-CAPolicies`, `Test-PolicyCompliance`, `Watch-PolicyDrift`, `Export-PolicyBaseline`

### 8.2 CAAClient vs CAAModule
- **Decision:** Follow AAM pattern naming — `CAAClient.psm1` for Dataverse module
- Private module handles: connection, environment variables, validation history, baselines

### 8.3 SupportsShouldProcess vs Custom -DryRun
- **Decision:** Migrate to `SupportsShouldProcess` + `-WhatIf` (standard PowerShell)
- Remove custom `-DryRun` parameter, or keep as alias to `-WhatIf` for backward compat
- AAM uses `SupportsShouldProcess` as the canonical pattern

### 8.4 Zone Lookup Adaptation
- AAM maps **environments** to zones
- CAA maps **security groups** to zones (since CA policies target groups)
- Zone lookup for CAA: Given an environment zone, resolve the corresponding security group ID from config
- ELM lookup is used when deploying policies to determine which templates map to which environments

### 8.5 Policy Drift Detection Approach
- **Baseline capture:** Snapshot all FSI CA policies (JSON export with timestamps)
- **Drift detection:** Compare current policies against baseline
- **Comparison dimensions:** state, conditions, grantControls, sessionControls
- **Severity mapping:** Follow ACV pattern (Passed=1, Warning=2, GracePeriod=3, Failed=4, Error=5)
- **Alert categories:** Policy disabled (Critical), Exclusion added (High), Control weakened (High), Timeout changed (Medium), Name changed (Low)
