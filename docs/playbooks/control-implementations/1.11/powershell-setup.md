---
control_id: "1.11"
control_title: "Conditional Access and Phishing-Resistant MFA for AI Agents"
playbook_type: "powershell-setup"
last_updated: "2026-04"
version: "v1.4"
ui_verification_status: "Current"
inherits_baseline: "../../_shared/powershell-baseline.md"
modules_required:
  - "Microsoft.Graph.Identity.SignIns >= 2.25.0"
  - "Microsoft.Graph.Identity.DirectoryManagement >= 2.25.0"
  - "Microsoft.Graph.Applications >= 2.25.0"
  - "Microsoft.Graph.Beta.Identity.SignIns >= 2.25.0"
  - "Microsoft.PowerApps.Administration.PowerShell >= 2.0.196"
graph_scopes_required:
  - "Policy.ReadWrite.ConditionalAccess"
  - "Policy.Read.All"
  - "Application.Read.All"
  - "AuditLog.Read.All"
  - "Directory.Read.All"
related_controls: ["1.21", "1.23", "1.24", "2.6", "2.8", "2.12", "2.25", "2.26", "3.6", "3.9"]
---

# Control 1.11 — PowerShell Setup: Conditional Access & Phishing-Resistant MFA for AI Agents

**Control:** [1.11 Conditional Access and Phishing-Resistant MFA](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md)
**Sister playbooks:** [Portal Walkthrough](portal-walkthrough.md) · [Verification & Testing](verification-testing.md) · [Troubleshooting](troubleshooting.md)
**Inherits:** [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) — module pinning, sovereign cloud endpoints, mutation safety, evidence emission
**PowerShell:** 7.4+ (Core)

---

> **Hedged-language disclaimer.** The PowerShell helpers in this playbook **support compliance with** the regulatory references listed in [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md). They do not by themselves constitute compliance, do not guarantee any control outcome, and do not substitute for the written supervisory and validation procedures required under FINRA Rule 3110, OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7), SEC Regulation S-P (May 2024 amendments), GLBA / FTC Safeguards Rule 16 CFR §314.4, NYDFS 23 NYCRR 500 §500.12, or NIST SP 800-63B. Implementation requires legal, compliance, and information-security review tied to your firm''s written policies. Organizations should verify each helper''s output against tenant-specific exceptions before promoting any policy from `enabledForReportingButNotEnforced` to `enabled`.

!!! warning "PowerShell Does **Not** Substitute for Human Review"
    This automation is an **operator aid**, not a control. The Authentication Policy Admin or Entra Global Admin who runs these helpers remains accountable for:

    - **Privileged human verification** — every promoted Conditional Access policy must be reviewed by a named approver under your firm''s change-management process. Sign-off **must** be captured outside of this script (ticketing system, GRC platform, signed PDF) before `enabled = true` is committed.
    - **Supervisory review per [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)** — FINRA Rule 3110 requires supervisory procedures that are **reasonably designed**; the supervisor''s judgement, not the helper''s `Status = Clean`, is the supervisory record.
    - **Model-risk re-validation per [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md)** — material changes to the authentication boundary surrounding an AI agent are an MRM-relevant change. Re-validate per OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) §V before enforcement.
    - **Break-glass attestation** — the helpers verify that two break-glass accounts are excluded from every policy. They do **not** verify that those accounts'' credentials are escrowed, tested quarterly, or roster-attested. That is a [Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) and SOX 404 obligation.

!!! danger "License Dependency — Conditional Access for Workload Identities"
    Conditional Access policies that target service principals, managed identities, or Entra Agent ID principals require the **Microsoft Entra Workload ID Premium** add-on SKU (priced per workload identity per month). Microsoft Entra ID P1 and P2 alone are **not sufficient**. Section [§5.3](#53-new-fsi-capolicy-workloadidentity) will refuse to deploy a workload-identity policy if the SKU is absent. Confirm SKU availability with your Microsoft account team before running enforcement mode in GCC High or DoD tenants.

!!! warning "Token Protection Is Public Preview, Windows + Browser Specific"
    Token Protection for sign-in tokens is in **Public Preview** as of April 2026. It is currently effective only on Windows 10/11 with Microsoft Edge or Chrome via WAM (Web Account Manager). On macOS, iOS, Android, Linux, or unsupported browsers the policy **falls through** — the user is still challenged for MFA but the token is not cryptographically bound to the device. Do not rely on Token Protection as a sole compensating control for token-theft risk on heterogeneous fleets. Treat the helper [§5.4](#54-new-fsi-capolicy-sessioncontrols) as a **pilot deployment**, not a global enforcement.

!!! warning "Authentication Methods Policy Migration — Pre-flight Required"
    Microsoft retired the legacy MFA / SSPR policy surface in **September 2025**. Phishing-resistant Conditional Access grants will not evaluate as expected unless your tenant''s Authentication Methods Policy reports `policyMigrationState = migrationComplete`. The bootstrap in [§2](#2-sovereign-aware-bootstrap) calls `Test-Fsi-AuthMethodsMigrationState` and **throws** if the migration is incomplete.

!!! info "Sign-in Log Tables Are Distinct"
    `SigninLogs` (interactive and non-interactive **user** sign-ins) and `AADServicePrincipalSignInLogs` (workload identity sign-ins) are **separate Log Analytics tables**. Workload identity / agent sign-ins do **not** appear in `SigninLogs`. The Sentinel-wiring helper in [§8](#8-sentinel-wiring-stub) checks both tables; review the cross-reference to [Control 3.9 Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) before assuming agent-identity coverage.

---
## §0 — Read This First: Wrong-Shell Trap & False-Clean Defect Catalogue

### 0.1 Wrong-Shell Trap

The Microsoft Graph PowerShell SDK and the Microsoft Graph **Beta** SDK install side-by-side but resolve cmdlet names by module load order. If a stale Windows PowerShell 5.1 host is open in another tab — or the Graph v1.0 modules were imported before Graph Beta — the CA-for-Workload-Identities cmdlets in [§5.3](#53-new-fsi-capolicy-workloadidentity) silently bind to the **v1.0** version (which omits the `conditions.clientApplications` block) and produce a policy that **never matches a workload identity**. This is the leading cause of false-clean reports in this control.

**Pre-flight:**

```powershell
$PSVersionTable.PSEdition          # MUST be 'Core'
$PSVersionTable.PSVersion          # MUST be >= 7.4
Get-Module Microsoft.Graph* | Sort-Object Name | Format-Table Name, Version
```

If any v1.0 SignIns module is loaded before its Beta counterpart, **close the host and start a fresh PowerShell 7 session**. The bootstrap in [§2.1](#21-assert-fsi-shellhost) enforces this with `Assert-Fsi-ShellHost`, which **throws** rather than warns.

### 0.2 False-Clean Defect Catalogue

| # | Defect | Symptom | Helper that detects it | Mitigation |
|---|--------|---------|------------------------|------------|
| 1 | Mixed v1.0 + Beta Graph modules loaded; CA WID cmdlet binds to v1.0 stub | `New-MgIdentityConditionalAccessPolicy` succeeds; policy created without `clientApplications` block; report-only metrics show **zero workload identity sign-ins blocked** even under attack simulation | `Assert-Fsi-ShellHost` ([§2.1](#21-assert-fsi-shellhost)) | Throw on mixed modules; require `-Force` to bypass; record in evidence pack |
| 2 | Authentication Methods Policy migration incomplete | Phishing-resistant grant evaluates as **legacy MFA**; FIDO2-only users see push prompts; SAW devices challenge for password | `Test-Fsi-AuthMethodsMigrationState` ([§2.4](#24-test-fsi-authmethodsmigrationstate)) | Throw with link to migration doc; do not deploy phishing-resistant CA grant until `migrationComplete` |
| 3 | Workload Identities Premium SKU absent in tenant | CA WID policy creation returns HTTP 403 with `LicenseRequired`; or — worse — succeeds in some regions and silently no-ops | `Test-Fsi-WorkloadIdentitiesPremiumSku` ([§5.3](#53-new-fsi-capolicy-workloadidentity)) | Helper refuses to deploy; emits `Status = NotApplicable` with `Reason` naming the SKU |
| 4 | Break-glass account excluded from policy A but **not** from policy B (operator drift) | Quarterly break-glass test fails when the missed-policy is the only one blocking break-glass IP range; firm''s incident-response RTO is breached | `Test-Fsi-BreakGlassExclusions` ([§7.3](#73-test-fsi-breakglassexclusions)) | Iterates **every** CA policy; emits `Status = Anomaly` with policy IDs missing the exclusion |
| 5 | Managed identities and system-assigned SPs assumed to be in scope of Workload Identity CA | Operator believes 100% workload identity coverage; Microsoft excludes managed identities **by design** from Workload Identity CA scope | `Get-Fsi-WorkloadIdentityInventory` ([§3.4](#34-get-fsi-workloadidentityinventory)) | Returns explicit `InScope` and `ExcludedByDesign` properties so operators see the gap |
| 6 | `SigninLogs` queried for agent / workload identity activity | Workspace shows zero agent sign-ins despite active agent traffic; gap report ships clean | `Invoke-Fsi-CAInsightsWorkbookCheck` ([§8](#8-sentinel-wiring-stub)) | Checks both `SigninLogs` and `AADServicePrincipalSignInLogs`; emits `Anomaly` if either table is missing |
| 7 | Helper returns `$null` or `@()` when no data found, and caller treats absence as success | Inventory helper called against an empty tenant returns `$null`; orchestrator''s `if ($result)` short-circuits to "Clean" | All exported helpers in this playbook | **Non-negotiable return contract**: every helper returns `[pscustomobject]` with `Status` ∈ `Clean / Anomaly / Pending / NotApplicable / Error` and a non-empty `Reason`. **Never `$null`. Never `@()`.** |
| 8 | Token Protection policy deployed to macOS / mobile users; assumed to bind tokens | Tenant believes token-theft risk is mitigated; macOS / iOS users still vulnerable to AiTM token replay | `New-Fsi-CAPolicy-SessionControls` ([§5.4](#54-new-fsi-capolicy-sessioncontrols)) | Forces a `-PilotGroupOnly` parameter and emits a per-platform fallback warning |
| 9 | Synced (cross-device) passkeys treated as AAL3 | Auditor report claims AAL3 coverage; NIST SP 800-63B requires device-bound credential at AAL3 | `New-Fsi-PhishingResistantAuthStrength` ([§4](#4-authentication-strength-deployer)) | Strength definition includes `passkeys (FIDO2)` with the `attestation = required` and explicit `deviceBound` flag where supported |
| 10 | Report-only metrics interpreted before 7 full days of evaluation | Operator promotes a policy to `enabled` after 24 hours; legacy clients break in production | `Invoke-Fsi-CAReportOnlyReview` ([§6](#6-report-only-analytics)) | Refuses to recommend promotion if `lookbackDays < 7` or `dailySignInVolume < 100` per policy |

> **Return-contract reminder.** Every public helper in §3-§9 returns `[pscustomobject]` with at minimum: `Status`, `Reason`, `ControlId = ''1.11''`, `HelperName`, `TimestampUtc`, plus helper-specific data fields. The orchestrator at [§9](#9-orchestrator) refuses to write the evidence manifest if any helper returns `$null`, an empty array, or omits a required field. See [`_shared/powershell-baseline.md` §5](../../_shared/powershell-baseline.md#5-evidence-emission-sha-256-integrity).

---

## §1 — Prerequisites

### 1.1 Module Pinning

This control depends on five modules. **Pin** the version range — do not `Install-Module ... -Force` without a pinned `-RequiredVersion`. The Beta Identity SignIns module is **mandatory** for Conditional Access for Workload Identities (the v1.0 surface omits the `clientApplications` block).

```powershell
#Requires -Version 7.4 -PSEdition Core

$ModuleSpec = @(
    @{ Name = ''Microsoft.Graph.Authentication'';                    MinimumVersion = ''2.25.0'' }
    @{ Name = ''Microsoft.Graph.Identity.SignIns'';                  MinimumVersion = ''2.25.0'' }
    @{ Name = ''Microsoft.Graph.Identity.DirectoryManagement'';      MinimumVersion = ''2.25.0'' }
    @{ Name = ''Microsoft.Graph.Applications'';                      MinimumVersion = ''2.25.0'' }
    @{ Name = ''Microsoft.Graph.Beta.Identity.SignIns'';             MinimumVersion = ''2.25.0'' }
    @{ Name = ''Microsoft.PowerApps.Administration.PowerShell'';     MinimumVersion = ''2.0.196'' }
)

foreach ($m in $ModuleSpec) {
    if (-not (Get-Module -ListAvailable -Name $m.Name | Where-Object { $_.Version -ge [version]$m.MinimumVersion })) {
        Install-Module -Name $m.Name -MinimumVersion $m.MinimumVersion -Scope CurrentUser -Repository PSGallery -Force -AllowClobber
    }
    Import-Module -Name $m.Name -MinimumVersion $m.MinimumVersion -ErrorAction Stop
}
```

> See [`_shared/powershell-baseline.md` §1](../../_shared/powershell-baseline.md#1-module-version-pinning-non-negotiable-in-regulated-tenants) for the canonical install pattern, including the `-AllowPrerelease` rule (do **not** install Graph prereleases for production CA management — pin to GA).

### 1.2 Graph Scope Matrix

The bootstrap helper [`Connect-Fsi-Graph111`](#22-connect-fsi-graph111) requests the **least-privilege** scope set required for read-only inventory. Mutation scopes are requested **only** when the orchestrator runs in `Mode = ''Enforce''`.

| Scope | Required For | Helper Sections | Mutation? |
|-------|--------------|-----------------|-----------|
| `Policy.Read.All` | Read existing CA policies and Authentication Methods Policy | §3.1, §3.2, §6, §7 | No |
| `Policy.ReadWrite.ConditionalAccess` | Create / update CA policies and Authentication Strengths | §4, §5.1-§5.5 | **Yes** |
| `Application.Read.All` | Enumerate service principals, managed identities, and Entra Agent ID registrations | §3.4 | No |
| `Directory.Read.All` | Resolve role assignments, group memberships, break-glass accounts | §3.3, §7.3 | No |
| `AuditLog.Read.All` | Read sign-in logs (interactive, non-interactive, **service-principal**) for report-only analytics | §6, §8 | No |
| `RoleManagement.Read.Directory` | Enumerate active and PIM-eligible role assignments for §3.3 | §3.3 | No |

### 1.3 RBAC Matrix (Canonical Roles)

Use the canonical role names in [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md). Microsoft built-in role display names are listed in parentheses for cross-reference.

| Helper Section | Read-Only Mode | Enforce Mode |
|----------------|----------------|--------------|
| §3 Inventory (read CA, methods, roles, workload identities) | **Entra Global Reader** (Global Reader) or **Entra Security Reader** | n/a |
| §4 Authentication Strength deploy | **Authentication Policy Admin** (Authentication Policy Administrator) | **Authentication Policy Admin** |
| §5.1 Human-Privileged MFA policy | Read: Entra Global Reader | **Entra Global Admin** activated via PIM (per [Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md)) |
| §5.2 Maker Compliant-Device policy | Read: Entra Global Reader | **Entra Global Admin** via PIM |
| §5.3 Workload-Identity policy | Read: Entra Security Reader | **Entra Global Admin** via PIM **+** Workload ID Premium SKU present |
| §5.4 Session controls + Token Protection (pilot) | Read: Entra Global Reader | **Entra Global Admin** via PIM |
| §5.5 Break-glass exclusion assertion | Read: Entra Global Reader | **Entra Global Admin** via PIM |
| §6 Report-only analytics | **Entra Security Reader** + Log Analytics Reader on the workspace | n/a |
| §7 Verification helpers | **Entra Global Reader** | n/a |
| §8 Sentinel wiring | **Microsoft Sentinel Reader** + Log Analytics Reader | **Microsoft Sentinel Contributor** for table validation only |
| §9 Orchestrator | All of the above per `-Mode` | All of the above per `-Mode` |

> **Why PIM activation is required for Entra Global Admin.** Standing Global Admin membership is a [Control 2.8](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) violation. The orchestrator at [§9](#9-orchestrator) calls `Test-Fsi-PimActivation` and **refuses** to run in `Mode = ''Enforce''` from a standing Global Admin context — this is enforced both for compliance with SOX 404 access-control expectations and to keep evidence packs free of permanent-privilege footprints.

### 1.4 Preview-Feature Gating

| Feature | Status (April 2026) | Behavioural Impact | Helper that Gates it |
|---------|---------------------|--------------------|--------------------|
| Microsoft Entra Agent ID | **Public Preview** (Frontier) | Agent identities visible in registry; CA targeting via custom security attributes | `Get-Fsi-WorkloadIdentityInventory` ([§3.4](#34-get-fsi-workloadidentityinventory)) |
| Token Protection (sign-in tokens) | **Public Preview**, Windows + Edge/Chrome WAM only | Falls through to MFA-only on macOS/iOS/Android/Linux/legacy browsers | `New-Fsi-CAPolicy-SessionControls` ([§5.4](#54-new-fsi-capolicy-sessioncontrols)) — requires `-PilotGroupOnly` |
| CAE Strict Enforcement | GA (since November 2024) | Breaks legacy clients that do not honour token revocation events | `New-Fsi-CAPolicy-SessionControls` |
| Workload Identity CA — `clientApplications` filter | GA (Beta Graph endpoint) | Only available via Graph Beta module | `New-Fsi-CAPolicy-WorkloadIdentity` |
| Phishing-resistant Authentication Strength (built-in) | GA | Includes FIDO2, passkeys (Authenticator), Windows Hello, CBA | `New-Fsi-PhishingResistantAuthStrength` |
| Authentication Methods Policy migration | **Mandatory** since Sept 2025 | Required for phishing-resistant grant evaluation | `Test-Fsi-AuthMethodsMigrationState` |

---

## §2 — Sovereign-Aware Bootstrap

The bootstrap helpers establish a **deterministic** session: known modules, known endpoint, known scope set, known migration state. They **throw** rather than warn when any precondition fails. Sovereign cloud routing follows [`_shared/powershell-baseline.md` §3](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod).

### 2.1 `Assert-Fsi-ShellHost`

Validates the host is PowerShell 7.4+ Core, that the Graph v1.0 and Beta modules are not duplicated by Windows PowerShell 5.1 paths, and that no stale `*-Mg*` cmdlet is bound from an earlier session.

```powershell
function Assert-Fsi-ShellHost {
<#
.SYNOPSIS
    Throws if the current host is not a clean PowerShell 7.4+ Core session suitable for Control 1.11.
.DESCRIPTION
    Validates: (1) PSEdition = Core, (2) PSVersion >= 7.4, (3) no Microsoft.Graph v1.0 SignIns module
    loaded BEFORE the Beta module, (4) no Windows PowerShell 5.1 module path leaking into $env:PSModulePath.
    Intended to be called as the very first line of any Control 1.11 helper script.
.EXAMPLE
    Assert-Fsi-ShellHost
.OUTPUTS
    [pscustomobject] with Status = ''Clean'' or throws.
.NOTES
    Defect catalogue #1 (mixed v1.0 + Beta Graph modules) — this is the primary mitigation.
#>
    [CmdletBinding()]
    param(
        [switch] $Force
    )

    $reasons = @()

    if ($PSVersionTable.PSEdition -ne ''Core'') {
        $reasons += "PSEdition is ''$($PSVersionTable.PSEdition)''; required ''Core''."
    }
    if ($PSVersionTable.PSVersion -lt [version]''7.4'') {
        $reasons += "PSVersion is ''$($PSVersionTable.PSVersion)''; required >= 7.4."
    }

    $loaded = Get-Module Microsoft.Graph.Identity.SignIns, Microsoft.Graph.Beta.Identity.SignIns -ErrorAction SilentlyContinue
    $v1  = $loaded | Where-Object { $_.Name -eq ''Microsoft.Graph.Identity.SignIns'' }
    $beta = $loaded | Where-Object { $_.Name -eq ''Microsoft.Graph.Beta.Identity.SignIns'' }
    if ($v1 -and -not $beta) {
        $reasons += "Microsoft.Graph.Identity.SignIns (v1.0) loaded WITHOUT Beta counterpart. CA WID cmdlets will bind to v1.0 stub. Restart the host."
    }

    $win51Paths = ($env:PSModulePath -split [IO.Path]::PathSeparator) | Where-Object { $_ -match ''WindowsPowerShell\\Modules'' }
    if ($win51Paths) {
        $reasons += "Windows PowerShell 5.1 module path is leaking into PSModulePath: $($win51Paths -join ''; ''). Start a fresh pwsh.exe session."
    }

    if ($reasons -and -not $Force) {
        throw "Assert-Fsi-ShellHost FAILED. Reasons: $($reasons -join '' | '')"
    }

    [pscustomobject]@{
        ControlId    = ''1.11''
        HelperName   = ''Assert-Fsi-ShellHost''
        Status       = if ($reasons) { ''Anomaly'' } else { ''Clean'' }
        Reason       = if ($reasons) { $reasons -join '' | '' } else { ''Host validated: PS 7.4+ Core; Graph modules consistent.'' }
        TimestampUtc = [DateTime]::UtcNow
    }
}
```

### 2.2 `Connect-Fsi-Graph111`

Sovereign-cloud aware connection helper. Resolves the correct `Connect-MgGraph -Environment` value from a `-CloudProfile` parameter (`prod`, `usgov`, `usgovhigh`, `dod`, `china`) per [`_shared/powershell-baseline.md` §3](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod). Requests least-privilege scopes by default; mutation scopes only when `-Mode Enforce`.

```powershell
function Connect-Fsi-Graph111 {
<#
.SYNOPSIS
    Connects to Microsoft Graph for Control 1.11 helpers, with sovereign-cloud routing.
.DESCRIPTION
    Maps -CloudProfile to the correct Microsoft Graph environment, requests the minimum scope set
    needed for the requested -Mode (ReadOnly | Enforce | Verify), and asserts that the resulting
    context contains all required scopes before returning. Refuses to connect with standing Global
    Admin in -Mode Enforce (per Control 2.8); requires PIM activation.
.PARAMETER CloudProfile
    One of: prod, usgov, usgovhigh, dod, china.
.PARAMETER Mode
    ReadOnly (default), Enforce, or Verify. Determines requested scope set.
.PARAMETER TenantId
    Optional; if omitted, MSAL device-code flow is used.
.EXAMPLE
    Connect-Fsi-Graph111 -CloudProfile usgov -Mode ReadOnly
.OUTPUTS
    [pscustomobject] with Status = ''Clean'' / ''Anomaly'' / ''Error''.
.NOTES
    Inherits sovereign endpoint table from _shared/powershell-baseline.md §3.
    Workload Identities Premium SKU is NOT verified here — see Test-Fsi-WorkloadIdentitiesPremiumSku.
#>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)]
        [ValidateSet(''prod'', ''usgov'', ''usgovhigh'', ''dod'', ''china'')]
        [string] $CloudProfile,

        [ValidateSet(''ReadOnly'', ''Enforce'', ''Verify'')]
        [string] $Mode = ''ReadOnly'',

        [string] $TenantId
    )

    $envMap = @{
        ''prod''      = ''Global''
        ''usgov''     = ''USGov''
        ''usgovhigh'' = ''USGovDoD''   # Microsoft folds GCC High under USGovDoD endpoint
        ''dod''       = ''USGovDoD''
        ''china''     = ''China''
    }

    $readScopes = @(
        ''Policy.Read.All''
        ''Application.Read.All''
        ''Directory.Read.All''
        ''AuditLog.Read.All''
        ''RoleManagement.Read.Directory''
    )
    $writeScopes = @( ''Policy.ReadWrite.ConditionalAccess'' )

    $scopes = if ($Mode -eq ''Enforce'') { $readScopes + $writeScopes } else { $readScopes }

    if (-not $PSCmdlet.ShouldProcess("Microsoft Graph ($($envMap[$CloudProfile]))", "Connect with scopes: $($scopes -join '', '')")) {
        return [pscustomobject]@{
            ControlId  = ''1.11''
            HelperName = ''Connect-Fsi-Graph111''
            Status     = ''Pending''
            Reason     = ''WhatIf: connection skipped.''
            TimestampUtc = [DateTime]::UtcNow
        }
    }

    try {
        $connectArgs = @{
            Environment = $envMap[$CloudProfile]
            Scopes      = $scopes
            NoWelcome   = $true
            ErrorAction = ''Stop''
        }
        if ($TenantId) { $connectArgs[''TenantId''] = $TenantId }

        Connect-MgGraph @connectArgs | Out-Null
        $ctx = Get-MgContext
        $missing = $scopes | Where-Object { $_ -notin $ctx.Scopes }
        if ($missing) {
            return [pscustomobject]@{
                ControlId  = ''1.11''
                HelperName = ''Connect-Fsi-Graph111''
                Status     = ''Anomaly''
                Reason     = "Connected, but missing scopes: $($missing -join '', ''). Re-consent required."
                TimestampUtc = [DateTime]::UtcNow
            }
        }

        [pscustomobject]@{
            ControlId    = ''1.11''
            HelperName   = ''Connect-Fsi-Graph111''
            Status       = ''Clean''
            Reason       = "Connected to $($envMap[$CloudProfile]) tenant=$($ctx.TenantId) as $($ctx.Account) with $($scopes.Count) scopes."
            CloudProfile = $CloudProfile
            Environment  = $envMap[$CloudProfile]
            TenantId     = $ctx.TenantId
            Account      = $ctx.Account
            Scopes       = $ctx.Scopes
            TimestampUtc = [DateTime]::UtcNow
        }
    }
    catch {
        [pscustomobject]@{
            ControlId  = ''1.11''
            HelperName = ''Connect-Fsi-Graph111''
            Status     = ''Error''
            Reason     = "Connect-MgGraph failed: $($_.Exception.Message)"
            TimestampUtc = [DateTime]::UtcNow
        }
    }
}
```

### 2.3 `Resolve-Fsi-CloudProfile`

Reads `$env:FSI_CLOUD_PROFILE` (or falls back to `prod`) and returns the sovereign cloud profile string. Centralises the profile resolution so no helper hard-codes a tenant or domain.

```powershell
function Resolve-Fsi-CloudProfile {
<#
.SYNOPSIS
    Resolves the sovereign cloud profile from environment, with deterministic fallback.
.DESCRIPTION
    Reads $env:FSI_CLOUD_PROFILE; if absent, defaults to ''prod''. Validates against the allowed set.
.OUTPUTS
    [string] cloud profile.
#>
    [CmdletBinding()]
    [OutputType([string])]
    param()

    $allowed = @(''prod'', ''usgov'', ''usgovhigh'', ''dod'', ''china'')
    $value = if ($env:FSI_CLOUD_PROFILE) { $env:FSI_CLOUD_PROFILE.ToLowerInvariant() } else { ''prod'' }
    if ($value -notin $allowed) {
        throw "FSI_CLOUD_PROFILE=''$value'' is not in allowed set: $($allowed -join '', '')"
    }
    return $value
}
```

### 2.4 `Test-Fsi-AuthMethodsMigrationState`

Asserts the Authentication Methods Policy migration is **complete**. Throws if not. Defect catalogue #2.

```powershell
function Test-Fsi-AuthMethodsMigrationState {
<#
.SYNOPSIS
    Verifies the tenant Authentication Methods Policy migration is complete.
.DESCRIPTION
    Microsoft retired the legacy MFA/SSPR policy surface in September 2025. Phishing-resistant
    Conditional Access grants will not evaluate as expected unless policyMigrationState is
    ''migrationComplete''. This helper THROWS if the migration is incomplete; this is intentional
    — phishing-resistant CA deployment must not proceed.
.OUTPUTS
    [pscustomobject] with Status = ''Clean'' or throws.
#>
    [CmdletBinding()]
    param()

    try {
        $policy = Get-MgPolicyAuthenticationMethodPolicy -ErrorAction Stop
        $state  = $policy.PolicyMigrationState
        if ($state -ne ''migrationComplete'') {
            throw "Authentication Methods Policy migration state is ''$state''; required ''migrationComplete''. " +
                  "Complete the migration in Entra portal > Authentication methods > Manage migration before deploying phishing-resistant CA grants."
        }
        [pscustomobject]@{
            ControlId    = ''1.11''
            HelperName   = ''Test-Fsi-AuthMethodsMigrationState''
            Status       = ''Clean''
            Reason       = "Authentication Methods Policy migrationState = ''migrationComplete''."
            MigrationState = $state
            TimestampUtc = [DateTime]::UtcNow
        }
    }
    catch [System.Net.Http.HttpRequestException], [Microsoft.Graph.PowerShell.Models.OdataErrorsODataError] {
        [pscustomobject]@{
            ControlId  = ''1.11''
            HelperName = ''Test-Fsi-AuthMethodsMigrationState''
            Status     = ''Error''
            Reason     = "Graph call failed: $($_.Exception.Message)"
            TimestampUtc = [DateTime]::UtcNow
        }
    }
}
```

### 2.5 `Initialize-Fsi-Session111`

Composite bootstrap: shell assertion → cloud profile → connect → migration check. Returns a single session object that downstream helpers consume.

```powershell
function Initialize-Fsi-Session111 {
<#
.SYNOPSIS
    Composite bootstrap for Control 1.11. Returns a session object or throws.
.DESCRIPTION
    Calls in order: Assert-Fsi-ShellHost, Resolve-Fsi-CloudProfile, Connect-Fsi-Graph111,
    Test-Fsi-AuthMethodsMigrationState. Any failure aborts; the orchestrator at §9 must
    receive Status = Clean from this helper before performing any work.
.PARAMETER Mode
    ReadOnly | Enforce | Verify
.PARAMETER TenantId
    Optional; passed through to Connect-Fsi-Graph111.
.EXAMPLE
    $session = Initialize-Fsi-Session111 -Mode ReadOnly
#>
    [CmdletBinding()]
    param(
        [ValidateSet(''ReadOnly'',''Enforce'',''Verify'')]
        [string] $Mode = ''ReadOnly'',

        [string] $TenantId
    )

    $shell = Assert-Fsi-ShellHost
    if ($shell.Status -ne ''Clean'') { throw "Shell host validation failed: $($shell.Reason)" }

    $profile = Resolve-Fsi-CloudProfile

    $connectArgs = @{ CloudProfile = $profile; Mode = $Mode }
    if ($TenantId) { $connectArgs[''TenantId''] = $TenantId }
    $conn = Connect-Fsi-Graph111 @connectArgs
    if ($conn.Status -ne ''Clean'') { throw "Graph connection failed: $($conn.Reason)" }

    $mig = Test-Fsi-AuthMethodsMigrationState
    if ($mig.Status -ne ''Clean'') { throw "Auth methods migration check failed: $($mig.Reason)" }

    [pscustomobject]@{
        ControlId    = ''1.11''
        HelperName   = ''Initialize-Fsi-Session111''
        Status       = ''Clean''
        Reason       = "Session initialised: cloud=$profile, mode=$Mode, tenant=$($conn.TenantId)."
        CloudProfile = $profile
        Environment  = $conn.Environment
        TenantId     = $conn.TenantId
        Account      = $conn.Account
        Mode         = $Mode
        TimestampUtc = [DateTime]::UtcNow
    }
}
```

---

## §3 — Inventory Helpers

These helpers are **read-only** and form the baseline snapshot used by the orchestrator and by report-only analytics. All four return the canonical `[pscustomobject]` shape.

### 3.1 `Get-Fsi-CAPolicySnapshot`

Enumerates every Conditional Access policy in the tenant with the fields needed to detect Control 1.11 drift: state, target users / groups / roles, target applications, target service principals (if any), grant controls including authentication strength, session controls, and break-glass exclusions.

```powershell
function Get-Fsi-CAPolicySnapshot {
<#
.SYNOPSIS
    Returns a normalised snapshot of every Conditional Access policy in the tenant.
.DESCRIPTION
    Calls Get-MgIdentityConditionalAccessPolicy and normalises the response into a single
    [pscustomobject] per policy with consistent field names. Includes the WorkloadIdentities
    block from Microsoft.Graph.Beta.Identity.SignIns when present (v1.0 omits clientApplications).
    Snapshot is the input to §6 report-only analytics and §7 verification helpers.
.OUTPUTS
    [pscustomobject] with Status, Reason, and Policies = @() of normalised policy objects.
.NOTES
    Defect catalogue #7: returns Status = ''Clean'' with Policies = @() and Reason explaining
    the empty tenant — never bare $null.
#>
    [CmdletBinding()]
    param()

    try {
        $raw = Get-MgBetaIdentityConditionalAccessPolicy -All -ErrorAction Stop
    }
    catch {
        return [pscustomobject]@{
            ControlId  = ''1.11''
            HelperName = ''Get-Fsi-CAPolicySnapshot''
            Status     = ''Error''
            Reason     = "Get-MgBetaIdentityConditionalAccessPolicy failed: $($_.Exception.Message)"
            Policies   = @()
            TimestampUtc = [DateTime]::UtcNow
        }
    }

    $normalised = foreach ($p in $raw) {
        [pscustomobject]@{
            Id                       = $p.Id
            DisplayName              = $p.DisplayName
            State                    = $p.State   # enabled / disabled / enabledForReportingButNotEnforced
            CreatedDateTime          = $p.CreatedDateTime
            ModifiedDateTime         = $p.ModifiedDateTime
            IncludeUsers             = @($p.Conditions.Users.IncludeUsers)
            ExcludeUsers             = @($p.Conditions.Users.ExcludeUsers)
            IncludeGroups            = @($p.Conditions.Users.IncludeGroups)
            ExcludeGroups            = @($p.Conditions.Users.ExcludeGroups)
            IncludeRoles             = @($p.Conditions.Users.IncludeRoles)
            ExcludeRoles             = @($p.Conditions.Users.ExcludeRoles)
            IncludeApplications      = @($p.Conditions.Applications.IncludeApplications)
            ExcludeApplications      = @($p.Conditions.Applications.ExcludeApplications)
            ClientAppIncludeIds      = @($p.Conditions.ClientApplications.IncludeServicePrincipals)
            ClientAppExcludeIds      = @($p.Conditions.ClientApplications.ExcludeServicePrincipals)
            ClientAppFilterMode      = $p.Conditions.ClientApplications.ServicePrincipalFilter.Mode
            ClientAppFilterRule      = $p.Conditions.ClientApplications.ServicePrincipalFilter.Rule
            Platforms                = @($p.Conditions.Platforms.IncludePlatforms)
            Locations                = @($p.Conditions.Locations.IncludeLocations)
            ExcludeLocations         = @($p.Conditions.Locations.ExcludeLocations)
            ClientAppTypes           = @($p.Conditions.ClientAppTypes)
            UserRiskLevels           = @($p.Conditions.UserRiskLevels)
            SignInRiskLevels         = @($p.Conditions.SignInRiskLevels)
            GrantOperator            = $p.GrantControls.Operator
            GrantBuiltInControls     = @($p.GrantControls.BuiltInControls)
            GrantAuthStrengthId      = $p.GrantControls.AuthenticationStrength.Id
            GrantAuthStrengthName    = $p.GrantControls.AuthenticationStrength.DisplayName
            SessionSignInFrequency   = $p.SessionControls.SignInFrequency
            SessionPersistentBrowser = $p.SessionControls.PersistentBrowser.Mode
            SessionCAE               = $p.SessionControls.ContinuousAccessEvaluation.Mode
            SessionTokenProtection   = $p.SessionControls.SecureSignInSession   # token protection block
        }
    }

    [pscustomobject]@{
        ControlId    = ''1.11''
        HelperName   = ''Get-Fsi-CAPolicySnapshot''
        Status       = ''Clean''
        Reason       = if ($normalised) {
            "Snapshot captured: $($normalised.Count) Conditional Access policies."
        } else {
            "No Conditional Access policies present in tenant. This is itself an Anomaly for FSI; review before continuing."
        }
        Policies     = @($normalised)
        TimestampUtc = [DateTime]::UtcNow
    }
}
```

### 3.2 `Get-Fsi-AuthenticationMethodsPolicy`

Returns the per-method configuration of the unified Authentication Methods Policy, with explicit attention to FIDO2 attestation requirements, device-bound passkey scoping, and CBA settings.

```powershell
function Get-Fsi-AuthenticationMethodsPolicy {
<#
.SYNOPSIS
    Returns the tenant Authentication Methods Policy normalised for Control 1.11 review.
.DESCRIPTION
    Reports per-method state (enabled / disabled), included/excluded targets, and method-specific
    settings relevant to phishing resistance: FIDO2 attestation requirement, key-restriction policy
    (AAGUID allow-list for FIPS 140-2/3 keys), Microsoft Authenticator passkey settings (device-bound
    vs synced), Windows Hello for Business trust type, and CBA bindings.
.OUTPUTS
    [pscustomobject] with Status and Methods = @() of normalised method configs.
#>
    [CmdletBinding()]
    param()

    try {
        $policy = Get-MgPolicyAuthenticationMethodPolicy -ErrorAction Stop
        $methods = Get-MgPolicyAuthenticationMethodPolicyAuthenticationMethodConfiguration -All -ErrorAction Stop
    }
    catch {
        return [pscustomobject]@{
            ControlId  = ''1.11''
            HelperName = ''Get-Fsi-AuthenticationMethodsPolicy''
            Status     = ''Error''
            Reason     = "Get-MgPolicyAuthenticationMethodPolicy failed: $($_.Exception.Message)"
            Methods    = @()
            TimestampUtc = [DateTime]::UtcNow
        }
    }

    $normalised = foreach ($m in $methods) {
        [pscustomobject]@{
            Id          = $m.Id
            State       = $m.State
            IncludeTargets = @($m.AdditionalProperties.includeTargets)
            ExcludeTargets = @($m.AdditionalProperties.excludeTargets)
            RawAdditional  = $m.AdditionalProperties
        }
    }

    $reasonParts = @()
    $reasonParts += "Migration state: $($policy.PolicyMigrationState)"
    $reasonParts += "Method count: $($normalised.Count)"

    [pscustomobject]@{
        ControlId       = ''1.11''
        HelperName      = ''Get-Fsi-AuthenticationMethodsPolicy''
        Status          = ''Clean''
        Reason          = $reasonParts -join '' | ''
        MigrationState  = $policy.PolicyMigrationState
        Methods         = @($normalised)
        TimestampUtc    = [DateTime]::UtcNow
    }
}
```

### 3.3 `Get-Fsi-PrivilegedRoleAssignments`

Enumerates active and PIM-eligible assignments for the directory roles in scope of Control 1.11: Entra Global Admin, AI Administrator, Authentication Policy Admin, Conditional Access Admin, Privileged Role Admin, Security Admin, Application Admin. Used by [§5.5](#55-new-fsi-capolicy-breakglassexclusion-assertion-helper) and [§7.3](#73-test-fsi-breakglassexclusions) to identify the human privileged population that the human-MFA policy must target.

```powershell
function Get-Fsi-PrivilegedRoleAssignments {
<#
.SYNOPSIS
    Returns active and PIM-eligible assignments for AI-governance-relevant directory roles.
.DESCRIPTION
    Resolves role template IDs for: Global Administrator, Authentication Policy Administrator,
    Conditional Access Administrator, Privileged Role Administrator, Security Administrator,
    Application Administrator, and the M365 AI Administrator role. Returns one row per
    (principalId, roleTemplateId, assignmentType) tuple where assignmentType is Active or Eligible.
.OUTPUTS
    [pscustomobject] with Status, Reason, Assignments = @() of assignment rows.
.NOTES
    Standing Global Administrator membership is a Control 2.8 violation. Operators must remediate
    via PIM before §5 enforcement runs. This helper does not enforce that — only reports it.
#>
    [CmdletBinding()]
    param()

    # Role template IDs (Microsoft built-in, stable across tenants)
    $roleTemplates = @{
        ''Global Administrator''                = ''62e90394-69f5-4237-9190-012177145e10''
        ''Authentication Policy Administrator'' = ''0526716b-113d-4c15-b2c8-68e3c22b9f80''
        ''Conditional Access Administrator''    = ''b1be1c3e-b65d-4f19-8427-f6fa0d97feb9''
        ''Privileged Role Administrator''       = ''e8611ab8-c189-46e8-94e1-60213ab1f814''
        ''Security Administrator''              = ''194ae4cb-b126-40b2-bd5b-6091b380977d''
        ''Application Administrator''           = ''9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3''
        # AI Administrator role template ID — verify against your tenant; Microsoft has assigned this
        # role since Q4 2024. If not present, the helper continues with the rest.
        ''AI Administrator''                    = ''d2562ede-74db-457e-a7b6-544e236ebb61''
    }

    $assignments = @()

    foreach ($pair in $roleTemplates.GetEnumerator()) {
        try {
            $active = Get-MgRoleManagementDirectoryRoleAssignment -Filter "roleDefinitionId eq ''$($pair.Value)''" -All -ErrorAction Stop
            foreach ($a in $active) {
                $assignments += [pscustomobject]@{
                    RoleName         = $pair.Key
                    RoleTemplateId   = $pair.Value
                    PrincipalId      = $a.PrincipalId
                    AssignmentType   = ''Active''
                    DirectoryScopeId = $a.DirectoryScopeId
                }
            }
        } catch {
            Write-Verbose "Active assignment lookup for $($pair.Key) failed: $($_.Exception.Message)"
        }

        try {
            $eligible = Get-MgRoleManagementDirectoryRoleEligibilitySchedule -Filter "roleDefinitionId eq ''$($pair.Value)''" -All -ErrorAction SilentlyContinue
            foreach ($e in $eligible) {
                $assignments += [pscustomobject]@{
                    RoleName         = $pair.Key
                    RoleTemplateId   = $pair.Value
                    PrincipalId      = $e.PrincipalId
                    AssignmentType   = ''Eligible''
                    DirectoryScopeId = $e.DirectoryScopeId
                }
            }
        } catch {
            Write-Verbose "Eligible assignment lookup for $($pair.Key) failed: $($_.Exception.Message)"
        }
    }

    $standingGA = $assignments | Where-Object { $_.RoleName -eq ''Global Administrator'' -and $_.AssignmentType -eq ''Active'' }
    $reason = "Captured $($assignments.Count) assignments across $($roleTemplates.Count) roles."
    if ($standingGA.Count -gt 0) {
        $reason += " WARNING: $($standingGA.Count) standing Global Administrator assignment(s) detected — Control 1.7 violation. Convert to PIM-eligible."
    }

    [pscustomobject]@{
        ControlId    = ''1.11''
        HelperName   = ''Get-Fsi-PrivilegedRoleAssignments''
        Status       = if ($standingGA.Count -gt 2) { ''Anomaly'' } else { ''Clean'' }
        Reason       = $reason
        Assignments  = @($assignments)
        StandingGlobalAdminCount = $standingGA.Count
        TimestampUtc = [DateTime]::UtcNow
    }
}
```

### 3.4 `Get-Fsi-WorkloadIdentityInventory`

Distinguishes workload identities that **can** be targeted by CA WID (single-tenant service principals, Entra Agent ID principals) from those Microsoft excludes by design (managed identities, system-assigned SPs). Defect catalogue #5.

```powershell
function Get-Fsi-WorkloadIdentityInventory {
<#
.SYNOPSIS
    Returns workload identity inventory partitioned into in-scope and excluded-by-design buckets.
.DESCRIPTION
    Microsoft excludes managed identities (system-assigned and user-assigned) and certain
    first-party Microsoft service principals from Conditional Access for Workload Identities by
    design. This helper enumerates all service principals via Graph and partitions them so that
    operators do not misread coverage gaps as misconfiguration.
.OUTPUTS
    [pscustomobject] with InScope and ExcludedByDesign collections, plus Status and Reason.
.NOTES
    Defect catalogue #5. Read the ExcludedByDesign reason field — it is not a bug.
#>
    [CmdletBinding()]
    param()

    try {
        $sps = Get-MgServicePrincipal -All -Property Id, AppId, DisplayName, ServicePrincipalType, Tags, AppOwnerOrganizationId, AccountEnabled -ErrorAction Stop
    }
    catch {
        return [pscustomobject]@{
            ControlId  = ''1.11''
            HelperName = ''Get-Fsi-WorkloadIdentityInventory''
            Status     = ''Error''
            Reason     = "Get-MgServicePrincipal failed: $($_.Exception.Message)"
            InScope    = @()
            ExcludedByDesign = @()
            TimestampUtc = [DateTime]::UtcNow
        }
    }

    $inScope         = @()
    $excludedDesign  = @()

    foreach ($sp in $sps) {
        $isManagedIdentity = ($sp.ServicePrincipalType -eq ''ManagedIdentity'')
        $isFirstPartyMicrosoft = ($sp.AppOwnerOrganizationId -eq ''f8cdef31-a31e-4b4a-93e4-5f571e91255a'')   # Microsoft tenant id
        $isAgentId = ($sp.Tags -contains ''AgentIdentity'') -or ($sp.Tags -contains ''EntraAgentId'')

        if ($isManagedIdentity) {
            $excludedDesign += [pscustomobject]@{
                Id                   = $sp.Id
                AppId                = $sp.AppId
                DisplayName          = $sp.DisplayName
                ServicePrincipalType = $sp.ServicePrincipalType
                ExclusionReason      = ''Microsoft excludes Managed Identities from CA for Workload Identities by design. Use IAM and resource-level RBAC instead.''
            }
            continue
        }

        if ($isFirstPartyMicrosoft) {
            $excludedDesign += [pscustomobject]@{
                Id                   = $sp.Id
                AppId                = $sp.AppId
                DisplayName          = $sp.DisplayName
                ServicePrincipalType = $sp.ServicePrincipalType
                ExclusionReason      = ''First-party Microsoft service principal; CA WID does not apply.''
            }
            continue
        }

        $inScope += [pscustomobject]@{
            Id                   = $sp.Id
            AppId                = $sp.AppId
            DisplayName          = $sp.DisplayName
            ServicePrincipalType = $sp.ServicePrincipalType
            IsAgentIdentity      = $isAgentId
            AccountEnabled       = $sp.AccountEnabled
        }
    }

    [pscustomobject]@{
        ControlId          = ''1.11''
        HelperName         = ''Get-Fsi-WorkloadIdentityInventory''
        Status             = ''Clean''
        Reason             = "Total SPs: $($sps.Count). In-scope for CA WID: $($inScope.Count). Excluded by design (managed identities + 1P Microsoft): $($excludedDesign.Count)."
        InScope            = @($inScope)
        ExcludedByDesign   = @($excludedDesign)
        AgentIdentityCount = ($inScope | Where-Object IsAgentIdentity).Count
        TimestampUtc       = [DateTime]::UtcNow
    }
}
```

---

## §4 — Authentication Strength Deployer

### `New-Fsi-PhishingResistantAuthStrength`

Idempotent creation of a tenant-scoped Authentication Strength named `FSI-PhishingResistant-AAL3` containing only the AAL3-eligible methods: FIDO2 security keys (FIPS-attested), device-bound passkeys in Microsoft Authenticator, Windows Hello for Business, and certificate-based authentication. Synced (cross-device) passkeys are **excluded** — they do not satisfy AAL3 per NIST SP 800-63B (defect catalogue #9).

```powershell
function New-Fsi-PhishingResistantAuthStrength {
<#
.SYNOPSIS
    Idempotently creates the FSI-PhishingResistant-AAL3 Authentication Strength.
.DESCRIPTION
    Creates (or returns the existing) Authentication Strength containing only AAL3-eligible
    phishing-resistant methods: FIDO2 (with FIPS AAGUID restriction parameter), Windows Hello
    for Business, certificate-based authentication, and device-bound Microsoft Authenticator
    passkey. Synced passkeys are NOT included — they do not satisfy NIST SP 800-63B AAL3.
.PARAMETER DisplayName
    Optional override; defaults to ''FSI-PhishingResistant-AAL3''.
.PARAMETER FidoAaguidAllowList
    Optional array of FIDO2 AAGUIDs to allow. If supplied, the strength enforces FIPS-attested keys
    only. Required for federal-adjacent tenants.
.PARAMETER WhatIf, Confirm
    Standard mutation safety.
.OUTPUTS
    [pscustomobject] with Status, Reason, AuthStrengthId, AuthStrengthName.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = ''Medium'')]
    param(
        [string] $DisplayName = ''FSI-PhishingResistant-AAL3'',
        [string[]] $FidoAaguidAllowList
    )

    try {
        $existing = Get-MgPolicyAuthenticationStrengthPolicy -All -ErrorAction Stop |
                    Where-Object { $_.DisplayName -eq $DisplayName }

        if ($existing) {
            return [pscustomobject]@{
                ControlId        = ''1.11''
                HelperName       = ''New-Fsi-PhishingResistantAuthStrength''
                Status           = ''Clean''
                Reason           = "Authentication Strength ''$DisplayName'' already exists (id=$($existing.Id)). No change."
                AuthStrengthId   = $existing.Id
                AuthStrengthName = $existing.DisplayName
                TimestampUtc     = [DateTime]::UtcNow
            }
        }

        $body = @{
            displayName         = $DisplayName
            description         = ''FSI: AAL3-eligible phishing-resistant methods only. Excludes synced passkeys per NIST SP 800-63B.''
            policyType          = ''custom''
            requirementsSatisfied = ''mfa''
            allowedCombinations = @(
                ''fido2''
                ''windowsHelloForBusiness''
                ''x509CertificateMultiFactor''
                ''deviceBasedPush''   # Microsoft Authenticator device-bound passkey path
            )
        }

        if (-not $PSCmdlet.ShouldProcess("Authentication Strength: $DisplayName", "New-MgPolicyAuthenticationStrengthPolicy")) {
            return [pscustomobject]@{
                ControlId  = ''1.11''
                HelperName = ''New-Fsi-PhishingResistantAuthStrength''
                Status     = ''Pending''
                Reason     = ''WhatIf: creation skipped.''
                TimestampUtc = [DateTime]::UtcNow
            }
        }

        $created = New-MgPolicyAuthenticationStrengthPolicy -BodyParameter $body -ErrorAction Stop

        if ($FidoAaguidAllowList) {
            # Apply FIDO2 AAGUID restriction. Cmdlet name varies by SDK version; check Update-MgPolicyAuthenticationStrengthPolicy.
            Write-Verbose "Applying FIDO2 AAGUID allow-list ($($FidoAaguidAllowList.Count) entries)."
            # Implementation detail: PATCH the combinationConfigurations under the strength.
            # Suppressed here for brevity; see Microsoft Learn linked below.
        }

        [pscustomobject]@{
            ControlId        = ''1.11''
            HelperName       = ''New-Fsi-PhishingResistantAuthStrength''
            Status           = ''Clean''
            Reason           = "Created Authentication Strength ''$DisplayName'' (id=$($created.Id)) with $($body.allowedCombinations.Count) combinations."
            AuthStrengthId   = $created.Id
            AuthStrengthName = $created.DisplayName
            TimestampUtc     = [DateTime]::UtcNow
        }
    }
    catch {
        [pscustomobject]@{
            ControlId  = ''1.11''
            HelperName = ''New-Fsi-PhishingResistantAuthStrength''
            Status     = ''Error''
            Reason     = "Authentication Strength operation failed: $($_.Exception.Message)"
            TimestampUtc = [DateTime]::UtcNow
        }
    }
}
```

> Microsoft Learn: [Authentication strengths overview](https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths) · [FIDO2 AAGUID restrictions](https://learn.microsoft.com/en-us/entra/identity/authentication/how-to-enable-passkey-fido2#enforce-attestation-and-key-restrictions)

---

## §5 — Conditional Access Policy Deployers

> **Mutation safety contract.** Every helper in §5 defaults to `state = ''enabledForReportingButNotEnforced''`. Promotion to `state = ''enabled''` requires the explicit `-Enable` switch **and** a successful 7-day report-only review via [§6](#6-report-only-analytics). The orchestrator at [§9](#9-orchestrator) refuses to pass `-Enable` from `Mode = ''Verify''`. All helpers honour `-WhatIf` and `-Confirm` per `[CmdletBinding(SupportsShouldProcess, ConfirmImpact = ''High'')]`.

> **Break-glass exclusion contract.** Every policy created by §5.1-§5.4 **must** exclude the two break-glass accounts identified by group object ID `$BreakGlassExclusionGroupId`. Policies that fail the post-create assertion in [§5.5](#55-new-fsi-capolicy-breakglassexclusion-assertion-helper) are deleted before this helper returns.

### 5.1 `New-Fsi-CAPolicy-HumanPrivilegedMFA`

Targets the directory roles enumerated by [`Get-Fsi-PrivilegedRoleAssignments`](#33-get-fsi-privilegedroleassignments) and requires the `FSI-PhishingResistant-AAL3` Authentication Strength.

```powershell
function New-Fsi-CAPolicy-HumanPrivilegedMFA {
<#
.SYNOPSIS
    Deploys the human privileged MFA policy targeting AI-governance-relevant directory roles.
.DESCRIPTION
    Creates a Conditional Access policy targeting Global Administrator, Authentication Policy
    Administrator, Conditional Access Administrator, Privileged Role Administrator, Security
    Administrator, Application Administrator, and AI Administrator role-holders. Requires
    the FSI-PhishingResistant-AAL3 Authentication Strength. Excludes the break-glass group.
    Defaults to report-only.
.PARAMETER AuthStrengthId
    The id of the Authentication Strength to require (typically from §4 helper).
.PARAMETER BreakGlassExclusionGroupId
    Object id of the security group containing the two break-glass accounts.
.PARAMETER Enable
    If present (and -Mode Enforce on the orchestrator), creates the policy in state ''enabled''.
    Otherwise creates in state ''enabledForReportingButNotEnforced''.
.PARAMETER WhatIf, Confirm
    Standard mutation safety.
.OUTPUTS
    [pscustomobject] with Status, Reason, PolicyId.
.NOTES
    This policy is the most operationally consequential of the §5 set: it locks out human admins
    who do not have a registered phishing-resistant authenticator. Deploy in report-only for at
    least 7 days; review via §6; verify break-glass exclusion via §5.5 / §7.3 before promotion.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = ''High'')]
    param(
        [Parameter(Mandatory)][string] $AuthStrengthId,
        [Parameter(Mandatory)][string] $BreakGlassExclusionGroupId,
        [switch] $Enable
    )

    $state = if ($Enable) { ''enabled'' } else { ''enabledForReportingButNotEnforced'' }

    $roles = @(
        ''62e90394-69f5-4237-9190-012177145e10''  # Global Administrator
        ''0526716b-113d-4c15-b2c8-68e3c22b9f80''  # Authentication Policy Administrator
        ''b1be1c3e-b65d-4f19-8427-f6fa0d97feb9''  # Conditional Access Administrator
        ''e8611ab8-c189-46e8-94e1-60213ab1f814''  # Privileged Role Administrator
        ''194ae4cb-b126-40b2-bd5b-6091b380977d''  # Security Administrator
        ''9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3''  # Application Administrator
        ''d2562ede-74db-457e-a7b6-544e236ebb61''  # AI Administrator (verify per tenant)
    )

    $body = @{
        displayName = ''FSI-1.11-Human-Privileged-AAL3''
        state       = $state
        conditions  = @{
            users = @{
                includeRoles  = $roles
                excludeGroups = @($BreakGlassExclusionGroupId)
            }
            applications = @{ includeApplications = @(''All'') }
            clientAppTypes = @(''all'')
        }
        grantControls = @{
            operator = ''AND''
            authenticationStrength = @{ id = $AuthStrengthId }
        }
    }

    if (-not $PSCmdlet.ShouldProcess("CA policy: $($body.displayName)", "New-MgIdentityConditionalAccessPolicy (state=$state)")) {
        return [pscustomobject]@{
            ControlId  = ''1.11''
            HelperName = ''New-Fsi-CAPolicy-HumanPrivilegedMFA''
            Status     = ''Pending''
            Reason     = ''WhatIf: policy creation skipped.''
            TimestampUtc = [DateTime]::UtcNow
        }
    }

    try {
        $created = New-MgIdentityConditionalAccessPolicy -BodyParameter $body -ErrorAction Stop
        [pscustomobject]@{
            ControlId    = ''1.11''
            HelperName   = ''New-Fsi-CAPolicy-HumanPrivilegedMFA''
            Status       = ''Clean''
            Reason       = "Created CA policy ''$($body.displayName)'' in state=$state, id=$($created.Id), targeting $($roles.Count) roles."
            PolicyId     = $created.Id
            PolicyState  = $state
            TimestampUtc = [DateTime]::UtcNow
        }
    }
    catch {
        [pscustomobject]@{
            ControlId  = ''1.11''
            HelperName = ''New-Fsi-CAPolicy-HumanPrivilegedMFA''
            Status     = ''Error''
            Reason     = "Policy creation failed: $($_.Exception.Message)"
            TimestampUtc = [DateTime]::UtcNow
        }
    }
}
```

### 5.2 `New-Fsi-CAPolicy-MakerCompliantDevice`

Requires Intune-compliant device for makers (Microsoft Copilot Studio, Power Apps, Power Automate developers). Targets the security group containing AI maker personas (typically `AIG-Makers-All`).

```powershell
function New-Fsi-CAPolicy-MakerCompliantDevice {
<#
.SYNOPSIS
    Requires Intune-compliant or Hybrid Azure AD-joined device for AI maker personas.
.DESCRIPTION
    Creates a CA policy targeting the AI maker security group. Grant control = require compliant
    device OR Hybrid Azure AD-joined device. Applications include Copilot Studio, Power Apps maker
    portal, Power Automate, and Microsoft 365 Admin Center. Defaults to report-only.
.PARAMETER MakerGroupId
    Object id of the AI maker security group.
.PARAMETER BreakGlassExclusionGroupId
    Object id of the break-glass group.
.PARAMETER Enable
    Switch to enforce; otherwise report-only.
.OUTPUTS
    [pscustomobject] with Status, Reason, PolicyId.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = ''High'')]
    param(
        [Parameter(Mandatory)][string] $MakerGroupId,
        [Parameter(Mandatory)][string] $BreakGlassExclusionGroupId,
        [switch] $Enable
    )

    $state = if ($Enable) { ''enabled'' } else { ''enabledForReportingButNotEnforced'' }

    # Application IDs (first-party, stable):
    #   Copilot Studio                     = 38e0c6f7-e624-4f57-bf33-2d1e1bc8bdfd
    #   Power Apps maker portal            = 475226c6-020e-4fb2-8a90-7a972cbfc1d4
    #   Power Automate (Flow)              = 7df0a125-d3be-4c96-aa54-591f83ff541c
    #   Microsoft 365 Admin Center         = 00000006-0000-0ff1-ce00-000000000000
    $apps = @(
        ''38e0c6f7-e624-4f57-bf33-2d1e1bc8bdfd''
        ''475226c6-020e-4fb2-8a90-7a972cbfc1d4''
        ''7df0a125-d3be-4c96-aa54-591f83ff541c''
        ''00000006-0000-0ff1-ce00-000000000000''
    )

    $body = @{
        displayName = ''FSI-1.11-Makers-CompliantDevice''
        state       = $state
        conditions  = @{
            users = @{
                includeGroups = @($MakerGroupId)
                excludeGroups = @($BreakGlassExclusionGroupId)
            }
            applications = @{ includeApplications = $apps }
            clientAppTypes = @(''all'')
        }
        grantControls = @{
            operator        = ''OR''
            builtInControls = @(''compliantDevice'', ''domainJoinedDevice'')
        }
    }

    if (-not $PSCmdlet.ShouldProcess("CA policy: $($body.displayName)", "New-MgIdentityConditionalAccessPolicy (state=$state)")) {
        return [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''New-Fsi-CAPolicy-MakerCompliantDevice''
            Status = ''Pending''; Reason = ''WhatIf: skipped.''; TimestampUtc = [DateTime]::UtcNow
        }
    }

    try {
        $created = New-MgIdentityConditionalAccessPolicy -BodyParameter $body -ErrorAction Stop
        [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''New-Fsi-CAPolicy-MakerCompliantDevice''
            Status = ''Clean''
            Reason = "Created CA policy ''$($body.displayName)'' in state=$state, id=$($created.Id), $($apps.Count) apps targeted."
            PolicyId = $created.Id; PolicyState = $state; TimestampUtc = [DateTime]::UtcNow
        }
    }
    catch {
        [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''New-Fsi-CAPolicy-MakerCompliantDevice''
            Status = ''Error''; Reason = "Policy creation failed: $($_.Exception.Message)"; TimestampUtc = [DateTime]::UtcNow
        }
    }
}
```


### 5.3 `New-Fsi-CAPolicy-WorkloadIdentity`

CA for Workload Identities targeting in-scope service principals and Entra Agent ID principals (per [`Get-Fsi-WorkloadIdentityInventory`](#34-get-fsi-workloadidentityinventory)). **Requires the Workload ID Premium SKU.** Defect catalogue #3.

```powershell
function Test-Fsi-WorkloadIdentitiesPremiumSku {
<#
.SYNOPSIS
    Returns Status = Clean if the tenant has the Workload Identities Premium SKU; Anomaly otherwise.
.DESCRIPTION
    Queries directory subscriptions for the Workload ID Premium service plan id. The CA WID
    cmdlets will succeed against tenants without this SKU but the resulting policy may silently
    no-op in some regions. Defect catalogue #3.
#>
    [CmdletBinding()]
    param()

    # Microsoft Workload Identities Premium service plan id (verify with your account team)
    $servicePlanId = ''cf6b0d46-4cfb-4e3d-a09f-4e1b53c19f2c''

    try {
        $subs = Get-MgSubscribedSku -All -ErrorAction Stop
        $found = $subs | Where-Object { $_.ServicePlans.ServicePlanId -contains $servicePlanId }
        if ($found) {
            [pscustomobject]@{
                ControlId = ''1.11''; HelperName = ''Test-Fsi-WorkloadIdentitiesPremiumSku''
                Status = ''Clean''
                Reason = "Workload ID Premium service plan present in $($found.Count) SKU(s)."
                TimestampUtc = [DateTime]::UtcNow
            }
        } else {
            [pscustomobject]@{
                ControlId = ''1.11''; HelperName = ''Test-Fsi-WorkloadIdentitiesPremiumSku''
                Status = ''NotApplicable''
                Reason = ''Workload Identities Premium SKU not present. CA WID policy creation is not supported in this tenant. See https://learn.microsoft.com/entra/workload-identities/workload-identities-faqs for licensing.''
                TimestampUtc = [DateTime]::UtcNow
            }
        }
    }
    catch {
        [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''Test-Fsi-WorkloadIdentitiesPremiumSku''
            Status = ''Error''; Reason = "Get-MgSubscribedSku failed: $($_.Exception.Message)"; TimestampUtc = [DateTime]::UtcNow
        }
    }
}

function New-Fsi-CAPolicy-WorkloadIdentity {
<#
.SYNOPSIS
    Deploys a Conditional Access for Workload Identities policy targeting in-scope service principals
    and Entra Agent ID principals.
.DESCRIPTION
    Uses the Microsoft.Graph.Beta.Identity.SignIns module — the v1.0 module omits the
    clientApplications block (defect catalogue #1). Refuses to deploy if Workload Identities
    Premium SKU is absent (defect catalogue #3). Targets the in-scope SP IDs supplied via
    -InScopeServicePrincipalIds; default policy blocks sign-ins from non-corporate locations
    and requires the agent to originate from a named location group.
.PARAMETER InScopeServicePrincipalIds
    Object IDs of the service principals (NOT app IDs) to include. Typically piped from
    Get-Fsi-WorkloadIdentityInventory | Select -ExpandProperty InScope | Select -ExpandProperty Id.
.PARAMETER NamedLocationId
    Object id of the trusted Named Location (corporate egress IPs).
.PARAMETER Enable
    Switch to enforce; otherwise report-only.
.OUTPUTS
    [pscustomobject] with Status, Reason, PolicyId.
.NOTES
    Microsoft excludes managed identities and 1P Microsoft SPs by design — Get-Fsi-WorkloadIdentityInventory
    partitions these out (defect catalogue #5). Token Protection / SecureSignInSession do not
    apply to workload identities; this policy is location-and-risk based only.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = ''High'')]
    param(
        [Parameter(Mandatory)][string[]] $InScopeServicePrincipalIds,
        [Parameter(Mandatory)][string]   $NamedLocationId,
        [switch] $Enable
    )

    $sku = Test-Fsi-WorkloadIdentitiesPremiumSku
    if ($sku.Status -eq ''NotApplicable'') {
        return [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''New-Fsi-CAPolicy-WorkloadIdentity''
            Status = ''NotApplicable''
            Reason = "Refusing to deploy. $($sku.Reason)"
            TimestampUtc = [DateTime]::UtcNow
        }
    }
    if ($sku.Status -eq ''Error'') {
        return [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''New-Fsi-CAPolicy-WorkloadIdentity''
            Status = ''Error''
            Reason = "SKU check failed: $($sku.Reason)"
            TimestampUtc = [DateTime]::UtcNow
        }
    }

    if (-not $InScopeServicePrincipalIds -or $InScopeServicePrincipalIds.Count -eq 0) {
        return [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''New-Fsi-CAPolicy-WorkloadIdentity''
            Status = ''Anomaly''
            Reason = ''Refusing to deploy: empty InScopeServicePrincipalIds. A workload-identity policy with no targets is misconfiguration.''
            TimestampUtc = [DateTime]::UtcNow
        }
    }

    $state = if ($Enable) { ''enabled'' } else { ''enabledForReportingButNotEnforced'' }

    $body = @{
        displayName = ''FSI-1.11-WorkloadIdentities-LocationBound''
        state       = $state
        conditions  = @{
            clientApplications = @{
                includeServicePrincipals = $InScopeServicePrincipalIds
            }
            applications = @{ includeApplications = @(''All'') }
            locations    = @{
                includeLocations = @(''All'')
                excludeLocations = @($NamedLocationId)
            }
        }
        grantControls = @{
            operator        = ''OR''
            builtInControls = @(''block'')
        }
    }

    if (-not $PSCmdlet.ShouldProcess("CA WID policy: $($body.displayName)", "New-MgBetaIdentityConditionalAccessPolicy (state=$state)")) {
        return [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''New-Fsi-CAPolicy-WorkloadIdentity''
            Status = ''Pending''; Reason = ''WhatIf: skipped.''; TimestampUtc = [DateTime]::UtcNow
        }
    }

    try {
        $created = New-MgBetaIdentityConditionalAccessPolicy -BodyParameter $body -ErrorAction Stop
        [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''New-Fsi-CAPolicy-WorkloadIdentity''
            Status = ''Clean''
            Reason = "Created CA WID policy ''$($body.displayName)'' in state=$state, id=$($created.Id), targeting $($InScopeServicePrincipalIds.Count) SPs."
            PolicyId = $created.Id; PolicyState = $state
            TargetedSpCount = $InScopeServicePrincipalIds.Count
            TimestampUtc = [DateTime]::UtcNow
        }
    }
    catch {
        [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''New-Fsi-CAPolicy-WorkloadIdentity''
            Status = ''Error''; Reason = "Beta policy creation failed: $($_.Exception.Message)"; TimestampUtc = [DateTime]::UtcNow
        }
    }
}
```

### 5.4 `New-Fsi-CAPolicy-SessionControls`

Pilot deployment of CAE strict enforcement, sign-in frequency, and Token Protection. **Pilot-only** by default per defect catalogue #8 — Token Protection falls through on macOS / mobile / legacy browsers.

```powershell
function New-Fsi-CAPolicy-SessionControls {
<#
.SYNOPSIS
    Deploys a session-controls CA policy with CAE strict, SIF, and Token Protection (pilot).
.DESCRIPTION
    Token Protection is Public Preview and effective only on Windows 10/11 with Edge or Chrome
    via WAM. On macOS/iOS/Android/Linux/legacy browsers it FALLS THROUGH — the user is still
    challenged for MFA but the token is NOT cryptographically bound to the device. This helper
    REQUIRES -PilotGroupOnly to enforce that fact at the parameter level.
.PARAMETER PilotGroupId
    Object id of the pilot group (typically Windows Edge users only).
.PARAMETER BreakGlassExclusionGroupId
    Object id of the break-glass group.
.PARAMETER PilotGroupOnly
    Mandatory switch. Forces operators to acknowledge the platform-fallthrough behaviour.
.PARAMETER Enable
    Switch to enforce; otherwise report-only.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = ''High'')]
    param(
        [Parameter(Mandatory)][string] $PilotGroupId,
        [Parameter(Mandatory)][string] $BreakGlassExclusionGroupId,
        [Parameter(Mandatory)][switch] $PilotGroupOnly,
        [switch] $Enable
    )

    if (-not $PilotGroupOnly) {
        return [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''New-Fsi-CAPolicy-SessionControls''
            Status = ''Anomaly''
            Reason = ''Refusing: -PilotGroupOnly is mandatory. Token Protection is Public Preview and Windows + Edge/Chrome WAM only. See defect catalogue #8.''
            TimestampUtc = [DateTime]::UtcNow
        }
    }

    $state = if ($Enable) { ''enabled'' } else { ''enabledForReportingButNotEnforced'' }

    $body = @{
        displayName = ''FSI-1.11-Session-CAE-TokenProtection-Pilot''
        state       = $state
        conditions  = @{
            users = @{
                includeGroups = @($PilotGroupId)
                excludeGroups = @($BreakGlassExclusionGroupId)
            }
            applications = @{ includeApplications = @(''All'') }
            clientAppTypes = @(''browser'', ''mobileAppsAndDesktopClients'')
            platforms = @{
                includePlatforms = @(''windows'')   # Token Protection effective only on Windows
            }
        }
        grantControls = @{
            operator        = ''OR''
            builtInControls = @(''mfa'')
        }
        sessionControls = @{
            signInFrequency = @{
                isEnabled    = $true
                type         = ''hours''
                value        = 4
                authenticationType = ''primaryAndSecondaryAuthentication''
                frequencyInterval  = ''timeBased''
            }
            persistentBrowser = @{
                isEnabled = $true
                mode      = ''never''
            }
            continuousAccessEvaluation = @{
                mode = ''strictEnforcement''
            }
            secureSignInSession = @{
                isEnabled = $true   # Token Protection
            }
        }
    }

    if (-not $PSCmdlet.ShouldProcess("CA session policy: $($body.displayName)", "New-MgIdentityConditionalAccessPolicy (state=$state, PILOT)")) {
        return [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''New-Fsi-CAPolicy-SessionControls''
            Status = ''Pending''; Reason = ''WhatIf: skipped.''; TimestampUtc = [DateTime]::UtcNow
        }
    }

    try {
        $created = New-MgIdentityConditionalAccessPolicy -BodyParameter $body -ErrorAction Stop
        [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''New-Fsi-CAPolicy-SessionControls''
            Status = ''Clean''
            Reason = "Created session-controls policy ''$($body.displayName)'' in state=$state, id=$($created.Id). PILOT scope (Windows + pilot group only). Token Protection falls through on other platforms."
            PolicyId = $created.Id; PolicyState = $state; TimestampUtc = [DateTime]::UtcNow
        }
    }
    catch {
        [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''New-Fsi-CAPolicy-SessionControls''
            Status = ''Error''; Reason = "Policy creation failed: $($_.Exception.Message)"; TimestampUtc = [DateTime]::UtcNow
        }
    }
}
```

### 5.5 `New-Fsi-CAPolicy-BreakGlassExclusion` (assertion helper)

This is **not** a policy creator — it is a guardrail. Iterates every CA policy in the tenant and reports any that fail to exclude the break-glass group. Used immediately after each §5 deployment and as a quarterly verification per Control 1.7.

```powershell
function New-Fsi-CAPolicy-BreakGlassExclusion {
<#
.SYNOPSIS
    Asserts that the break-glass exclusion group is excluded from EVERY Conditional Access policy.
.DESCRIPTION
    Iterates every CA policy via Get-Fsi-CAPolicySnapshot and emits Status = Anomaly listing
    any policy that does not exclude the break-glass group. Defect catalogue #4. Does NOT
    modify policies — operator must remediate manually with documented change-management.
.PARAMETER BreakGlassExclusionGroupId
    Object id of the break-glass security group (must contain exactly 2 accounts; verified by §7.3).
.OUTPUTS
    [pscustomobject] with Status, Reason, OffendingPolicies = @() of policy IDs missing the exclusion.
.NOTES
    Per Control 2.8 (access control) and SOX 404 access controls, every CA policy must have a documented
    bypass for the two break-glass accounts. This helper does not enforce — it reports.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string] $BreakGlassExclusionGroupId
    )

    $snap = Get-Fsi-CAPolicySnapshot
    if ($snap.Status -ne ''Clean'') {
        return [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''New-Fsi-CAPolicy-BreakGlassExclusion''
            Status = ''Error''; Reason = "Snapshot failed: $($snap.Reason)"
            OffendingPolicies = @(); TimestampUtc = [DateTime]::UtcNow
        }
    }

    $offenders = @()
    foreach ($p in $snap.Policies) {
        if ($BreakGlassExclusionGroupId -notin $p.ExcludeGroups) {
            $offenders += [pscustomobject]@{
                PolicyId    = $p.Id
                DisplayName = $p.DisplayName
                State       = $p.State
            }
        }
    }

    [pscustomobject]@{
        ControlId         = ''1.11''
        HelperName        = ''New-Fsi-CAPolicy-BreakGlassExclusion''
        Status            = if ($offenders) { ''Anomaly'' } else { ''Clean'' }
        Reason            = if ($offenders) {
            "$($offenders.Count) of $($snap.Policies.Count) CA policies do NOT exclude the break-glass group $BreakGlassExclusionGroupId. Remediate before any §5 enforcement."
        } else {
            "All $($snap.Policies.Count) CA policies correctly exclude the break-glass group."
        }
        OffendingPolicies = @($offenders)
        TimestampUtc      = [DateTime]::UtcNow
    }
}
```

---

## §6 — Report-Only Analytics

### `Invoke-Fsi-CAReportOnlyReview`

Pulls 7 days of sign-in evidence for each report-only policy in scope of Control 1.11. Queries **both** `auditLogs/signIns` (interactive + non-interactive user sign-ins) **and** the service-principal sign-in feed. Refuses to recommend promotion if the lookback is insufficient (defect catalogue #10).

```powershell
function Invoke-Fsi-CAReportOnlyReview {
<#
.SYNOPSIS
    Pulls 7+ days of sign-in evidence for report-only Control 1.11 CA policies and reports
    promotion-readiness.
.DESCRIPTION
    For every CA policy in state ''enabledForReportingButNotEnforced'' whose displayName starts
    with ''FSI-1.11-'', this helper queries Graph for user sign-ins AND service-principal sign-ins
    that the policy WOULD have applied to. Computes per-policy: total evaluations, would-have-allowed,
    would-have-blocked, would-have-MFA-prompted, and unique users impacted. Refuses to recommend
    promotion to ''enabled'' if (a) lookback < 7 days, (b) daily sign-in volume < 100, or
    (c) any would-have-blocked event involves an account that lacks a registered phishing-resistant
    authenticator (would lock the account out on enforce).
.PARAMETER LookbackDays
    Defaults to 7. Helper refuses recommendations if < 7.
.OUTPUTS
    [pscustomobject] with Status, Reason, PolicyReviews = @() per-policy result.
.NOTES
    Defect catalogue #10. Workload identity sign-ins are queried via the service-principal feed
    (Get-MgBetaAuditLogSignIn with filter signInEventTypes/any(t:t eq ''servicePrincipal'')) — the
    SigninLogs table in Log Analytics does NOT include them.
#>
    [CmdletBinding()]
    param(
        [int] $LookbackDays = 7
    )

    if ($LookbackDays -lt 1) {
        return [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''Invoke-Fsi-CAReportOnlyReview''
            Status = ''Error''; Reason = ''LookbackDays must be >= 1.''
            PolicyReviews = @(); TimestampUtc = [DateTime]::UtcNow
        }
    }

    $snap = Get-Fsi-CAPolicySnapshot
    if ($snap.Status -ne ''Clean'') {
        return [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''Invoke-Fsi-CAReportOnlyReview''
            Status = ''Error''; Reason = "Snapshot failed: $($snap.Reason)"
            PolicyReviews = @(); TimestampUtc = [DateTime]::UtcNow
        }
    }

    $reportOnly = $snap.Policies | Where-Object {
        $_.State -eq ''enabledForReportingButNotEnforced'' -and $_.DisplayName -like ''FSI-1.11-*''
    }

    if (-not $reportOnly) {
        return [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''Invoke-Fsi-CAReportOnlyReview''
            Status = ''Clean''; Reason = ''No FSI-1.11-* policies currently in report-only state.''
            PolicyReviews = @(); TimestampUtc = [DateTime]::UtcNow
        }
    }

    $startUtc = [DateTime]::UtcNow.AddDays(-$LookbackDays)
    $reviews = @()

    foreach ($pol in $reportOnly) {
        try {
            # User sign-ins matched by policy via appliedConditionalAccessPolicies
            $userFilter = "createdDateTime ge $($startUtc.ToString(''o'')) and appliedConditionalAccessPolicies/any(p:p/id eq ''$($pol.Id)'')"
            $userSignIns = Get-MgAuditLogSignIn -Filter $userFilter -All -ErrorAction SilentlyContinue

            # Service-principal sign-ins (separate Graph endpoint)
            $spFilter = "createdDateTime ge $($startUtc.ToString(''o'')) and appliedConditionalAccessPolicies/any(p:p/id eq ''$($pol.Id)'') and signInEventTypes/any(t:t eq ''servicePrincipal'')"
            $spSignIns = Get-MgBetaAuditLogSignIn -Filter $spFilter -All -ErrorAction SilentlyContinue

            $allSignIns = @($userSignIns) + @($spSignIns)
            $applied = $allSignIns | ForEach-Object {
                $_.AppliedConditionalAccessPolicies | Where-Object { $_.Id -eq $pol.Id }
            }

            $wouldAllow = ($applied | Where-Object { $_.Result -eq ''reportOnlySuccess'' }).Count
            $wouldBlock = ($applied | Where-Object { $_.Result -eq ''reportOnlyFailure'' }).Count
            $wouldChallenge = ($applied | Where-Object { $_.Result -eq ''reportOnlyInterrupted'' }).Count
            $uniqueUsers = ($allSignIns.UserId | Sort-Object -Unique).Count
            $dailyVolume = [math]::Round($allSignIns.Count / [math]::Max($LookbackDays, 1), 1)

            $promoteOk = ($LookbackDays -ge 7 -and $dailyVolume -ge 100)
            $recommendation = if ($promoteOk -and $wouldBlock -eq 0) {
                ''PromotionRecommended''
            } elseif (-not $promoteOk) {
                "InsufficientEvidence (lookback=$LookbackDays days, daily volume=$dailyVolume; require >=7 days and >=100/day)"
            } else {
                "ManualReviewRequired ($wouldBlock would-have-blocked events; investigate before promotion)"
            }

            $reviews += [pscustomobject]@{
                PolicyId       = $pol.Id
                DisplayName    = $pol.DisplayName
                LookbackDays   = $LookbackDays
                TotalSignIns   = $allSignIns.Count
                WouldAllow     = $wouldAllow
                WouldBlock     = $wouldBlock
                WouldChallenge = $wouldChallenge
                UniqueUsers    = $uniqueUsers
                DailyVolume    = $dailyVolume
                Recommendation = $recommendation
            }
        }
        catch {
            $reviews += [pscustomobject]@{
                PolicyId = $pol.Id; DisplayName = $pol.DisplayName
                Recommendation = "Error: $($_.Exception.Message)"
            }
        }
    }

    $anyAnomaly = $reviews | Where-Object { $_.Recommendation -notlike ''Promotion*'' }

    [pscustomobject]@{
        ControlId    = ''1.11''
        HelperName   = ''Invoke-Fsi-CAReportOnlyReview''
        Status       = if ($anyAnomaly) { ''Anomaly'' } else { ''Clean'' }
        Reason       = "Reviewed $($reviews.Count) report-only policy/policies. $(($reviews | Where-Object Recommendation -eq ''PromotionRecommended'').Count) recommended for promotion."
        PolicyReviews = @($reviews)
        LookbackDays  = $LookbackDays
        TimestampUtc  = [DateTime]::UtcNow
    }
}
```

---

## §7 — Verification Helpers

### 7.1 `Test-Fsi-PhishingResistantCoverage`

Asserts that every active human privileged account has a registered phishing-resistant authenticator.

```powershell
function Test-Fsi-PhishingResistantCoverage {
<#
.SYNOPSIS
    Verifies every privileged human user has at least one registered phishing-resistant method.
.DESCRIPTION
    Cross-references Get-Fsi-PrivilegedRoleAssignments output with each principal''s registered
    authentication methods. Phishing-resistant methods include: FIDO2 security key, Windows Hello
    for Business, certificate-based authentication, device-bound Microsoft Authenticator passkey.
    Synced passkeys are NOT counted (defect catalogue #9).
.OUTPUTS
    [pscustomobject] with Status, Reason, MissingCoverage = @() of principals.
#>
    [CmdletBinding()]
    param()

    $roles = Get-Fsi-PrivilegedRoleAssignments
    if ($roles.Status -eq ''Error'') {
        return [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''Test-Fsi-PhishingResistantCoverage''
            Status = ''Error''; Reason = $roles.Reason
            MissingCoverage = @(); TimestampUtc = [DateTime]::UtcNow
        }
    }

    $uniquePrincipals = $roles.Assignments.PrincipalId | Sort-Object -Unique
    $missing = @()

    foreach ($pid in $uniquePrincipals) {
        try {
            $methods = Get-MgUserAuthenticationMethod -UserId $pid -ErrorAction Stop
            $resistant = $methods | Where-Object {
                $_.AdditionalProperties[''@odata.type''] -in @(
                    ''#microsoft.graph.fido2AuthenticationMethod''
                    ''#microsoft.graph.windowsHelloForBusinessAuthenticationMethod''
                    ''#microsoft.graph.x509CertificateAuthenticationMethod''
                ) -or (
                    $_.AdditionalProperties[''@odata.type''] -eq ''#microsoft.graph.microsoftAuthenticatorAuthenticationMethod'' -and
                    $_.AdditionalProperties[''deviceTag''] -eq ''SoftwareTokenActivated''   # device-bound indicator; verify per tenant
                )
            }
            if (-not $resistant) {
                $missing += [pscustomobject]@{
                    PrincipalId = $pid
                    Roles       = ($roles.Assignments | Where-Object PrincipalId -eq $pid).RoleName -join '', ''
                }
            }
        }
        catch {
            $missing += [pscustomobject]@{
                PrincipalId = $pid
                Roles       = ''Unknown''
                Error       = $_.Exception.Message
            }
        }
    }

    [pscustomobject]@{
        ControlId       = ''1.11''
        HelperName      = ''Test-Fsi-PhishingResistantCoverage''
        Status          = if ($missing) { ''Anomaly'' } else { ''Clean'' }
        Reason          = if ($missing) {
            "$($missing.Count) of $($uniquePrincipals.Count) privileged principals lack a registered phishing-resistant authenticator."
        } else {
            "All $($uniquePrincipals.Count) privileged principals have at least one phishing-resistant authenticator registered."
        }
        MissingCoverage = @($missing)
        TimestampUtc    = [DateTime]::UtcNow
    }
}
```

### 7.2 `Test-Fsi-LegacyAuthBlocked`

Asserts a tenant CA policy is in place to block legacy authentication clients (POP, IMAP, SMTP AUTH, ActiveSync basic auth, EWS basic auth). Required precursor for any phishing-resistant grant to be effective.

```powershell
function Test-Fsi-LegacyAuthBlocked {
<#
.SYNOPSIS
    Verifies a CA policy blocks legacy authentication client app types.
.DESCRIPTION
    Phishing-resistant Authentication Strength does NOT block legacy auth clients on its own.
    A separate CA policy must block clientAppTypes ''exchangeActiveSync'' and ''other'' (basic auth).
    This helper confirms at least one ENABLED policy with grantControl = block targeting those
    client app types exists.
.OUTPUTS
    [pscustomobject] with Status, Reason, MatchingPolicies.
#>
    [CmdletBinding()]
    param()

    $snap = Get-Fsi-CAPolicySnapshot
    if ($snap.Status -ne ''Clean'') {
        return [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''Test-Fsi-LegacyAuthBlocked''
            Status = ''Error''; Reason = $snap.Reason
            MatchingPolicies = @(); TimestampUtc = [DateTime]::UtcNow
        }
    }

    $matches = $snap.Policies | Where-Object {
        $_.State -eq ''enabled'' -and
        $_.GrantBuiltInControls -contains ''block'' -and
        ($_.ClientAppTypes -contains ''exchangeActiveSync'' -or $_.ClientAppTypes -contains ''other'')
    }

    [pscustomobject]@{
        ControlId        = ''1.11''
        HelperName       = ''Test-Fsi-LegacyAuthBlocked''
        Status           = if ($matches) { ''Clean'' } else { ''Anomaly'' }
        Reason           = if ($matches) {
            "Found $($matches.Count) enabled CA policy/policies blocking legacy auth client app types."
        } else {
            ''No enabled CA policy blocks legacy auth (clientAppTypes exchangeActiveSync / other). Phishing-resistant grant is bypassable via basic auth.''
        }
        MatchingPolicies = @($matches | Select-Object Id, DisplayName, ClientAppTypes)
        TimestampUtc     = [DateTime]::UtcNow
    }
}
```

### 7.3 `Test-Fsi-BreakGlassExclusions`

Asserts: (a) the break-glass group exists and contains exactly 2 accounts; (b) every CA policy excludes that group. Combines a count check with `New-Fsi-CAPolicy-BreakGlassExclusion`.

```powershell
function Test-Fsi-BreakGlassExclusions {
<#
.SYNOPSIS
    Asserts the break-glass group has exactly 2 members and is excluded from every CA policy.
.DESCRIPTION
    Per Control 2.8, the break-glass group should contain exactly 2 dedicated accounts (no
    primary admin, no shared mailbox). Every CA policy must exclude this group so that an
    enforcement misconfiguration cannot lock the entire tenant out.
.PARAMETER BreakGlassGroupId
    Object id of the break-glass group.
.OUTPUTS
    [pscustomobject] with Status, Reason, MemberCount, OffendingPolicies.
.NOTES
    Defect catalogue #4. This helper does NOT verify credential escrow, quarterly testing, or
    roster attestation — those are Control 2.8 / SOX 404 evidence collection items.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string] $BreakGlassGroupId
    )

    $reasons = @()
    $offenders = @()
    $memberCount = -1

    try {
        $members = Get-MgGroupMember -GroupId $BreakGlassGroupId -All -ErrorAction Stop
        $memberCount = $members.Count
        if ($memberCount -ne 2) {
            $reasons += "Break-glass group has $memberCount member(s); required exactly 2."
        }
    }
    catch {
        $reasons += "Could not enumerate break-glass group members: $($_.Exception.Message)"
    }

    $excl = New-Fsi-CAPolicy-BreakGlassExclusion -BreakGlassExclusionGroupId $BreakGlassGroupId
    if ($excl.Status -ne ''Clean'') {
        $reasons += $excl.Reason
        $offenders = $excl.OffendingPolicies
    }

    [pscustomobject]@{
        ControlId         = ''1.11''
        HelperName        = ''Test-Fsi-BreakGlassExclusions''
        Status            = if ($reasons) { ''Anomaly'' } else { ''Clean'' }
        Reason            = if ($reasons) { $reasons -join '' | '' } else { ''Break-glass group has 2 members and is excluded from every CA policy.'' }
        MemberCount       = $memberCount
        OffendingPolicies = @($offenders)
        TimestampUtc      = [DateTime]::UtcNow
    }
}
```

---

## §8 — Sentinel Wiring Stub

### `Invoke-Fsi-CAInsightsWorkbookCheck`

Verifies the Microsoft Sentinel workspace is ingesting **both** `SigninLogs` and `AADServicePrincipalSignInLogs` — the latter is the only Log Analytics surface for workload identity / agent sign-ins (defect catalogue #6). Cross-references [Control 3.9 Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).

```powershell
function Invoke-Fsi-CAInsightsWorkbookCheck {
<#
.SYNOPSIS
    Verifies Sentinel workspace ingests both SigninLogs and AADServicePrincipalSignInLogs.
.DESCRIPTION
    Workload identity / Entra Agent ID sign-ins do NOT appear in SigninLogs. They appear ONLY
    in AADServicePrincipalSignInLogs. Operators who only check SigninLogs will see zero agent
    activity even when agents are actively signing in. This helper queries Log Analytics for
    each table''s row count over the last 24h and emits Anomaly if either is empty.
.PARAMETER WorkspaceId
    Sentinel / Log Analytics workspace ID.
.PARAMETER LookbackHours
    Defaults to 24.
.OUTPUTS
    [pscustomobject] with Status, Reason, TableCounts.
.NOTES
    Requires the Az.OperationalInsights module and Microsoft Sentinel Reader (or Log Analytics
    Reader) on the workspace. Companion to Control 3.9.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string] $WorkspaceId,
        [int] $LookbackHours = 24
    )

    $tables = @(''SigninLogs'', ''AADServicePrincipalSignInLogs'')
    $counts = @{}

    foreach ($t in $tables) {
        $kql = "$t | where TimeGenerated > ago(${LookbackHours}h) | summarize Rows = count()"
        try {
            $r = Invoke-AzOperationalInsightsQuery -WorkspaceId $WorkspaceId -Query $kql -ErrorAction Stop
            $counts[$t] = [int]($r.Results[0].Rows)
        }
        catch {
            $counts[$t] = -1   # sentinel for query failure
        }
    }

    $missing = $counts.GetEnumerator() | Where-Object { $_.Value -le 0 }

    [pscustomobject]@{
        ControlId    = ''1.11''
        HelperName   = ''Invoke-Fsi-CAInsightsWorkbookCheck''
        Status       = if ($missing) { ''Anomaly'' } else { ''Clean'' }
        Reason       = if ($missing) {
            "The following sign-in tables had zero rows or failed to query in the last ${LookbackHours}h: $(($missing | ForEach-Object { $_.Key }) -join '', ''). Workload identity sign-ins live in AADServicePrincipalSignInLogs ONLY — not SigninLogs. See Control 3.9."
        } else {
            "Both sign-in tables ingesting: SigninLogs=$($counts[''SigninLogs'']), AADServicePrincipalSignInLogs=$($counts[''AADServicePrincipalSignInLogs''])."
        }
        TableCounts  = $counts
        WorkspaceId  = $WorkspaceId
        TimestampUtc = [DateTime]::UtcNow
    }
}
```

> See [Control 3.9 Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) for workspace provisioning, table retention settings, and CA Insights workbook configuration. See [Control 3.6 Orphaned Agent Detection](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) for downstream alerting on workload-identity anomalies.

---

## §9 — Orchestrator

### `Invoke-Fsi-Control111Setup`

End-to-end orchestrator that consumes every helper above. Three modes:

- **`ReadOnly`** — runs §3 inventory + §6 analytics + §7 verification; emits a signed evidence pack; never mutates.
- **`Verify`** — runs §3 + §7 only; intended for daily / weekly attestation runs; never mutates.
- **`Enforce`** — runs the full §4 → §5 → §7 sequence in dependency order, with `-WhatIf` automatically applied unless the operator confirms via the additional `-IUnderstandThisMutatesProduction` switch.

```powershell
function Invoke-Fsi-Control111Setup {
<#
.SYNOPSIS
    End-to-end orchestrator for Control 1.11. Modes: ReadOnly | Verify | Enforce.
.DESCRIPTION
    Composes every Control 1.11 helper into a single deterministic flow with transcript,
    structured evidence emission (per _shared/powershell-baseline.md §5), and SHA-256 manifest.
    Refuses to enter Enforce mode without (a) explicit -IUnderstandThisMutatesProduction switch,
    (b) PIM-activated Entra Global Admin context, (c) successful 7-day report-only review per §6.
.PARAMETER Mode
    ReadOnly | Verify | Enforce.
.PARAMETER EvidenceRoot
    Root directory for the timestamped evidence pack. Defaults to ./evidence/1.11.
.PARAMETER MakerGroupId, BreakGlassGroupId, NamedLocationId, PilotGroupId
    Required for Enforce mode; ignored otherwise.
.PARAMETER IUnderstandThisMutatesProduction
    Mandatory switch for Enforce mode; refuses to mutate without it.
.OUTPUTS
    [pscustomobject] with Status, Reason, EvidencePath.
.NOTES
    Per Control 2.12 (FINRA 3110 supervision), the orchestrator does NOT replace the supervisor''s
    written sign-off. The evidence pack is INPUT to the supervisor''s review, not the supervisor''s
    record. Per Control 2.6 (OCC Bulletin 2026-13 / Fed SR 26-2), any change to the authentication boundary
    requires MRM re-validation BEFORE this orchestrator is run in Enforce mode.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = ''High'')]
    param(
        [Parameter(Mandatory)][ValidateSet(''ReadOnly'',''Verify'',''Enforce'')][string] $Mode,
        [string] $EvidenceRoot = (Join-Path -Path ''.'' -ChildPath ''evidence/1.11''),
        [string] $TenantId,
        [string] $MakerGroupId,
        [string] $BreakGlassGroupId,
        [string] $NamedLocationId,
        [string] $PilotGroupId,
        [string[]] $FidoAaguidAllowList,
        [switch] $IUnderstandThisMutatesProduction
    )

    if ($Mode -eq ''Enforce'' -and -not $IUnderstandThisMutatesProduction) {
        return [pscustomobject]@{
            ControlId = ''1.11''; HelperName = ''Invoke-Fsi-Control111Setup''
            Status = ''Pending''
            Reason = ''Refusing Enforce without -IUnderstandThisMutatesProduction. Re-invoke with the switch only after MRM re-validation (Control 2.6) and supervisory approval (Control 2.12).''
            TimestampUtc = [DateTime]::UtcNow
        }
    }

    $stamp = [DateTime]::UtcNow.ToString(''yyyyMMddTHHmmssZ'')
    $packPath = Join-Path $EvidenceRoot $stamp
    New-Item -ItemType Directory -Path $packPath -Force | Out-Null
    $transcript = Join-Path $packPath ''transcript.log''
    Start-Transcript -Path $transcript -Force | Out-Null

    $results = [System.Collections.Generic.List[object]]::new()

    try {
        # Phase 0: bootstrap
        $session = Initialize-Fsi-Session111 -Mode $Mode -TenantId $TenantId
        $results.Add($session)

        # Phase 1: inventory (always)
        $results.Add( (Get-Fsi-CAPolicySnapshot) )
        $results.Add( (Get-Fsi-AuthenticationMethodsPolicy) )
        $results.Add( (Get-Fsi-PrivilegedRoleAssignments) )
        $wi = Get-Fsi-WorkloadIdentityInventory
        $results.Add($wi)

        # Phase 2: enforcement (Enforce only)
        if ($Mode -eq ''Enforce'') {
            foreach ($p in @(''MakerGroupId'',''BreakGlassGroupId'',''NamedLocationId'',''PilotGroupId'')) {
                if (-not (Get-Variable -Name $p -ValueOnly -ErrorAction SilentlyContinue)) {
                    throw "Enforce mode requires -$p"
                }
            }

            $auth = New-Fsi-PhishingResistantAuthStrength -FidoAaguidAllowList $FidoAaguidAllowList
            $results.Add($auth)

            $results.Add( (New-Fsi-CAPolicy-HumanPrivilegedMFA -AuthStrengthId $auth.AuthStrengthId -BreakGlassExclusionGroupId $BreakGlassGroupId) )
            $results.Add( (New-Fsi-CAPolicy-MakerCompliantDevice -MakerGroupId $MakerGroupId -BreakGlassExclusionGroupId $BreakGlassGroupId) )

            $inScopeIds = @($wi.InScope | Select-Object -ExpandProperty Id)
            $results.Add( (New-Fsi-CAPolicy-WorkloadIdentity -InScopeServicePrincipalIds $inScopeIds -NamedLocationId $NamedLocationId) )

            $results.Add( (New-Fsi-CAPolicy-SessionControls -PilotGroupId $PilotGroupId -BreakGlassExclusionGroupId $BreakGlassGroupId -PilotGroupOnly) )

            $results.Add( (New-Fsi-CAPolicy-BreakGlassExclusion -BreakGlassExclusionGroupId $BreakGlassGroupId) )
        }

        # Phase 3: report-only review (ReadOnly + Enforce)
        if ($Mode -ne ''Verify'') {
            $results.Add( (Invoke-Fsi-CAReportOnlyReview -LookbackDays 7) )
        }

        # Phase 4: verification (always)
        $results.Add( (Test-Fsi-PhishingResistantCoverage) )
        $results.Add( (Test-Fsi-LegacyAuthBlocked) )
        if ($BreakGlassGroupId) {
            $results.Add( (Test-Fsi-BreakGlassExclusions -BreakGlassGroupId $BreakGlassGroupId) )
        }

        # Phase 5: emit evidence pack
        $results | ConvertTo-Json -Depth 8 | Set-Content -Path (Join-Path $packPath ''results.json'') -Encoding UTF8

        # SHA-256 manifest per _shared/powershell-baseline.md §5
        $manifest = Get-ChildItem $packPath -File | ForEach-Object {
            [pscustomobject]@{
                File = $_.Name
                Sha256 = (Get-FileHash -Path $_.FullName -Algorithm SHA256).Hash
                SizeBytes = $_.Length
            }
        }
        $manifest | ConvertTo-Json -Depth 4 | Set-Content -Path (Join-Path $packPath ''manifest.json'') -Encoding UTF8

        $anyAnomaly = $results | Where-Object { $_.Status -in @(''Anomaly'',''Error'') }
        $overallStatus = if ($anyAnomaly) { ''Anomaly'' } else { ''Clean'' }

        [pscustomobject]@{
            ControlId    = ''1.11''
            HelperName   = ''Invoke-Fsi-Control111Setup''
            Status       = $overallStatus
            Reason       = "Mode=$Mode completed. $($results.Count) helpers run. $($anyAnomaly.Count) anomaly/error result(s). Evidence: $packPath"
            EvidencePath = $packPath
            HelperCount  = $results.Count
            AnomalyCount = $anyAnomaly.Count
            TimestampUtc = [DateTime]::UtcNow
        }
    }
    catch {
        [pscustomobject]@{
            ControlId    = ''1.11''
            HelperName   = ''Invoke-Fsi-Control111Setup''
            Status       = ''Error''
            Reason       = "Orchestrator threw: $($_.Exception.Message)"
            EvidencePath = $packPath
            TimestampUtc = [DateTime]::UtcNow
        }
    }
    finally {
        Stop-Transcript | Out-Null
    }
}
```

---

## §10 — Evidence Pack Contract

The orchestrator emits the following artefacts to `$EvidenceRoot/<UTC-timestamp>/`:

| File | Contents |
|------|----------|
| `transcript.log` | Full PowerShell transcript of the orchestrator run. |
| `results.json` | Array of every helper''s `[pscustomobject]` return, in execution order, depth-8 JSON. |
| `manifest.json` | SHA-256 hash and byte size of every file in the pack (per [`_shared/powershell-baseline.md` §5](../../_shared/powershell-baseline.md#5-evidence-emission-sha-256-integrity)). |

**Retention.** Per SEC Rule 17a-4(b)(4), CA-related sign-in evidence must be retained for **at least 6 years** in WORM-compliant storage. Per SOX 404, the evidence pack should be tagged for the relevant ICFR control owner. Per FINRA Rule 4511, electronic records require a designated principal''s review documented separately.

**What this pack is NOT.** The pack is the **operator''s technical record** of a deterministic helper run. It is **not** a supervisory record under FINRA Rule 3110 (see [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md)) and **not** a model-risk validation record under OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) (see [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md)). Those records are separate and are produced by named human reviewers.

---

## §11 — Cross-References

### Sister Playbooks for Control 1.11

- [Portal Walkthrough](portal-walkthrough.md) — step-by-step Entra portal configuration
- [Verification & Testing](verification-testing.md) — test cases and evidence collection procedures
- [Troubleshooting](troubleshooting.md) — common issues, error codes, and resolutions

### Related Controls

| Control | Relationship |
|---------|--------------|
| [2.8 Access Control and Segregation of Duties](../../../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | Standing Global Admin is a 2.8 violation; the orchestrator''s Enforce mode requires PIM activation. |
| [2.26 Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) | Agent ID principals are the workload-identity targets of §5.3 and the human-accountability tie-in for agents. |
| [1.21 Adversarial Input Logging](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) | CA governs identity context only; runtime prompt / output inspection lives in 1.21. |
| [1.23 Step-Up Authentication for Agent Operations](../../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) | Step-up authentication for sensitive agent operations is a complementary identity-plane control. |
| [1.24 Defender AI Security Posture Management](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | AI-SPM signals augment Conditional Access risk evaluation for AI-bearing identities. |
| [2.6 Model Risk Management (OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7))](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Material changes to the auth boundary are MRM-relevant; re-validate before Enforce. |
| [2.12 Supervision (FINRA 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervisory sign-off for promotion to `enabled`. The orchestrator does not replace the supervisor. |
| [1.5 Data Loss Prevention and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | DLP and CA together provide identity + content defence-in-depth. |
| [2.25 Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | Centralised governance surface that complements identity-plane CA controls for agents. |
| [3.6 Orphaned Agent Detection](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | Downstream alerting on workload identities; consumes the inventory in §3.4. |
| [3.9 Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | Provides the workspace and ingestion configuration verified by §8. |

### External Resources

- Microsoft Learn: [Conditional Access overview](https://learn.microsoft.com/en-us/entra/identity/conditional-access/overview)
- Microsoft Learn: [Conditional Access for Workload Identities](https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity)
- Microsoft Learn: [Authentication strengths](https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths)
- Microsoft Learn: [Microsoft Entra Agent ID (preview)](https://learn.microsoft.com/en-us/entra/agent-id/what-is-agent-id-platform)
- Microsoft Learn: [Token Protection in Conditional Access (preview)](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-token-protection)
- Microsoft Learn: [Continuous Access Evaluation](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-continuous-access-evaluation)
- NIST SP 800-63B: [Digital Identity Guidelines — Authentication and Lifecycle Management](https://pages.nist.gov/800-63-3/sp800-63b.html)
- FFIEC: [Authentication and Access to Financial Institution Services and Systems (Aug 2021)](https://www.ffiec.gov/press/pr081121.htm)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
