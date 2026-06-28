# Control 4.7 — PowerShell Setup: M365 Copilot Data Governance

> **Companion documents:** [Control 4.7](../../../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) · [Portal Walkthrough](portal-walkthrough.md) · [Verification & Testing](verification-testing.md) · [Troubleshooting](troubleshooting.md) · [PowerShell Baseline](../../_shared/powershell-baseline.md)
>
> **Audience:** Microsoft 365 administrators in US financial services responsible for Microsoft 365 Copilot grounding, prompt protection, retention, and search scope.
>
> **Scope:** Programmatic configuration of Microsoft Purview Information Protection labels, Microsoft Purview Data Loss Prevention (DLP) policies for the `MicrosoftCopilotExperience` workload, Microsoft Purview Endpoint DLP for browser-based pasteToCopilot restrictions, Restricted SharePoint Search (RSS), Copilot Pages and Notebooks retention, and multi-geo grounding scope.
>
> **Regulatory framing.** This playbook helps support compliance with **SEC 17a-3/17a-4** (records of communications and immutable retention), **SEC Regulation S-P (May 2024 amendments)** (incident notice and customer information safeguards), **FINRA Rule 4511** (general books and records), **FINRA Rule 3110** (supervision), **FINRA RN 24-09 / Rule 3110** (AI guidance), **GLBA Section 501(b)** (Safeguards Rule), **NYDFS 23 NYCRR 500.12** (multi-factor authentication and access governance), **SOX Section 302/404** (internal control over financial reporting), **OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12)** (model risk management), and **Federal Reserve SR 26-2 (formerly SR 11-7)** (model risk management). It does not, on its own, satisfy any regulation. Implementation correctness, retention, monitoring, and human supervision must be verified against your obligations.
>
> **Hedged language reminder:** Throughout this playbook the phrases "supports", "helps meet", "aids in", and "required for" are used in place of "ensures compliance" or "guarantees".
>
> **Roles required (canonical).** Entra Global Admin (one-time consent), Purview Compliance Admin (labels, DLP, retention), SharePoint Admin (RSS, multi-geo), Microsoft 365 Copilot administrator role for tenant-level Copilot policy in the Microsoft 365 admin center.
>
> **Apr 2026 subprocessor notice.** This playbook targets the Microsoft Commercial/Global cloud. Anthropic Claude is an enabled-by-default subprocessor for selected Researcher and Microsoft Copilot Studio scenarios in Commercial, is **disabled by default in EU/EFTA/UK** tenants, and is not available in EU/EFTA/UK tenants without explicit opt-in. Anthropic processing occurs **outside the EU Data Boundary**.

---

## 0. Wrong-shell trap and false-clean defects

Microsoft 365 Copilot governance touches **PnP.PowerShell v2** (SharePoint Embedded, Copilot Pages container management), **ExchangeOnlineManagement v3+** (Security & Compliance PowerShell — `Connect-IPPSSession`), and the **Microsoft.Graph v2** SDK. PnP.PowerShell v2 and ExchangeOnlineManagement v3+ are **PowerShell 7.4 LTS or later only** and will silently mis-bind, no-op, or return stale cached state if loaded into Windows PowerShell 5.1.

This is the **single most common false-clean defect**: an operator runs the playbook in 5.1, the `Connect-*` calls succeed (they fall through to legacy paths), `Get-*` calls return cached or empty results, and the validator reports "no policy required" — leaving the tenant unprotected.

The bootstrap (§2) hard-fails with **exit code 2** if any of the following is true:

- `$PSVersionTable.PSVersion.Major -lt 7` or (`Major -eq 7 -and Minor -lt 4`)
- `$PSVersionTable.PSEdition -ne 'Core'`
- `Get-Module -ListAvailable PnP.PowerShell` reports a v1.x assembly only
- `Get-Module -ListAvailable ExchangeOnlineManagement` reports a version below 3.5.0

```powershell
if ($PSVersionTable.PSEdition -ne 'Core' -or $PSVersionTable.PSVersion -lt [Version]'7.4.0') {
    Write-Error "Agt47: PowerShell 7.4+ Core required. Current: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion). Install from https://aka.ms/PowerShell. Exiting fail-closed."
    exit 2
}
```

**Other false-clean traps you must guard against:**

- **PnP v1 still on PSModulePath.** Even in PS 7.4, if a stale v1 assembly loads first (`Import-Module PnP.PowerShell -RequiredVersion 1.12.0` from a prior session), Copilot Pages container cmdlets are missing. Validate with `(Get-Module PnP.PowerShell).Version.Major -eq 2`.
- **Microsoft.Graph autoload of v1.** A user-scope `Microsoft.Graph 1.x` install can preempt the system-wide v2 install. Pin with `-RequiredVersion` (§1).
- **Cached delegated tokens.** A previous interactive Graph session can mask a missing app role. Always run `Disconnect-MgGraph` in the session opener.

- **"Set-LabelPolicy succeeded" with no actual rule change.** `Set-LabelPolicy` returns success when only metadata fields change, leaving the rule body untouched. The mutation pattern in §4 always re-reads via `Get-LabelPolicy` and verifies the field after the change.

> **Reminder:** This playbook is a programmatic complement to the [PowerShell Baseline](../../_shared/powershell-baseline.md). Section numbers in the baseline are referenced inline (BL-§1 = module pinning, BL-§2 = edition, BL-§3 = mutation safety, BL-§4 = SHA-256 evidence).

---

## 1. Module install and version pinning

Microsoft 365 Copilot governance requires five modules. All five are pinned with `-RequiredVersion` to suppress automatic upgrades and to make evidence reproducible. See [BL-§1](../../_shared/powershell-baseline.md#1-module-version-pinning-non-negotiable-in-regulated-tenants) for the rationale.

| Module | Required version | Purpose |
|---|---|---|
| `Microsoft.Graph` | 2.25.0 (or current GA 2.x) | Tenant entitlement, license inventory, role assignments |
| `Microsoft.Graph.Beta` | 2.25.0 (or current GA 2.x) | Beta-only Copilot endpoints (`copilotAdmin`, agent inventory) |
| `Microsoft.Online.SharePoint.PowerShell` | 16.0.26002.12000 | Restricted SharePoint Search, multi-geo |
| `ExchangeOnlineManagement` | 3.7.0 | Security & Compliance PowerShell (labels, DLP, retention) |
| `PnP.PowerShell` | 2.12.0 | SharePoint Embedded container management for Copilot Pages/Notebooks |

```powershell
$Required = @(
    @{ Name = 'Microsoft.Graph';                          Version = '2.25.0'        }
    @{ Name = 'Microsoft.Graph.Beta';                     Version = '2.25.0'        }
    @{ Name = 'Microsoft.Online.SharePoint.PowerShell';   Version = '16.0.26002.12000' }
    @{ Name = 'ExchangeOnlineManagement';                 Version = '3.7.0'         }
    @{ Name = 'PnP.PowerShell';                           Version = '2.12.0'        }
)

foreach ($m in $Required) {
    $installed = Get-Module -ListAvailable -Name $m.Name |
                 Where-Object { $_.Version -eq [Version]$m.Version }
    if (-not $installed) {
        Install-Module -Name $m.Name -RequiredVersion $m.Version -Scope CurrentUser -Force -AllowClobber -ErrorAction Stop
    }
    Import-Module $m.Name -RequiredVersion $m.Version -Force -ErrorAction Stop
    Write-Host "Loaded $($m.Name) $((Get-Module $m.Name).Version)"
}
```

**Why pinning matters for FSI evidence.** SEC 17a-4(f) and FINRA 4511 require records to be reproducible. If a future audit asks "what cmdlet surface was used in the April 2026 baseline?" the manifest must answer with exact module versions. A floating install (`Install-Module ... -Force` with no `-RequiredVersion`) cannot satisfy this.

**Module update governance.** Module bumps are change-managed under Control 2.7 (Change Management). Update the version table in this playbook, run the validator (§10) against a non-production tenant, capture before/after evidence, and submit a change record before promoting to production. Do not allow ad-hoc `Update-Module` in production tenants.

---

## 2. Bootstrap: `Initialize-Agt47Session`

The bootstrap validates the shell and modules, opens authenticated sessions to Graph, the Security & Compliance Center (IPPS), SharePoint Online, and PnP, and emits a session manifest. It is the **only entry point** for every other function in this playbook.

```powershell
function Initialize-Agt47Session {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='Medium')]
    param(
        [Parameter(Mandatory)] [string] $TenantId,
        [Parameter(Mandatory)] [string] $TenantDomainPrefix,
        [Parameter(Mandatory)] [string] $EvidenceRoot,
        [string] $RunId = (Get-Date -Format 'yyyyMMdd-HHmmss')
    )

    if ($PSVersionTable.PSEdition -ne 'Core' -or $PSVersionTable.PSVersion -lt [Version]'7.4.0') {
        Write-Error "Agt47: PowerShell 7.4+ Core required. Exiting fail-closed."; exit 2
    }

    $spoAdminUrl = "https://$TenantDomainPrefix-admin.sharepoint.com"
    $sessionDir  = Join-Path $EvidenceRoot "agt47-$RunId"
    $null = New-Item -ItemType Directory -Path $sessionDir -Force

    Disconnect-MgGraph -ErrorAction SilentlyContinue | Out-Null
    Connect-MgGraph -TenantId $TenantId -Environment 'Global' -Scopes @(
        'Directory.Read.All','Policy.Read.All','RoleManagement.Read.Directory',
        'InformationProtectionPolicy.Read','User.Read.All'
    ) -NoWelcome

    Connect-Agt47Compliance
    Connect-Agt47SharePoint -SpoAdminUrl $spoAdminUrl
    Connect-PnPOnline -Url $spoAdminUrl -Interactive -AzureEnvironment 'Production' | Out-Null

    $session = [pscustomobject]@{
        RunId        = $RunId
        Cloud        = 'Commercial'
        TenantId     = $TenantId
        SpoAdminUrl  = $spoAdminUrl
        SessionDir   = $sessionDir
        StartedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        ShellEdition = $PSVersionTable.PSEdition
        ShellVersion = $PSVersionTable.PSVersion.ToString()
        Modules      = (Get-Module Microsoft.Graph,Microsoft.Graph.Beta,Microsoft.Online.SharePoint.PowerShell,ExchangeOnlineManagement,PnP.PowerShell |
                          Select-Object Name,Version)
    }
    $session | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $sessionDir 'session.json') -Encoding utf8
    return $session
}

function Connect-Agt47Compliance {
    Connect-IPPSSession -ShowBanner:$false
}

function Connect-Agt47SharePoint {
    param([Parameter(Mandatory)] [string] $SpoAdminUrl)
    Connect-SPOService -Url $SpoAdminUrl
}
```

**Why a single bootstrap.** Every state-changing function in this playbook (`Set-Agt47*`) refuses to run unless `$script:Agt47Session` is populated by `Initialize-Agt47Session`. This guarantees that shell validation, evidence-folder creation, and module pinning occur exactly once per run, and that every mutation is recorded against a single `RunId`.

---
## 3. Pre-flight gates: `Test-Agt47Prerequisites`

Pre-flight gates are mandatory. They run after the bootstrap and before any mutation, and they fail closed if any of the following are missing.

| Gate | Verifies | Fail-closed exit |
|---|---|---|
| License inventory | At least one assigned `Microsoft_365_Copilot` SKU | exit 2 |
| RBAC: Compliance Administrator | Caller holds the role required for label and DLP cmdlets | exit 2 |
| RBAC: SharePoint Administrator | Caller holds the role required for `Set-SPOTenant` and RSS cmdlets | exit 2 |
| Cmdlet surface: RSS | `Set-SPOTenant` exposes `-RestrictedSearchApplicableToAllSites` (preferred) OR `Set-SPOTenantRestrictedSearchMode` is present (fallback) | exit 2 |
| Cmdlet surface: DLP for Copilot | `New-DlpComplianceRule` accepts `-Workload MicrosoftCopilotExperience` | exit 2 |
| Multi-geo posture | `Get-SPOMultiGeoExperience` returns a stable result if multi-geo is enabled | exit 1 (warn) |

```powershell
function Test-Agt47Prerequisites {
    [CmdletBinding()]
    param([Parameter(Mandatory)] $Session)

    $issues = @()

    # License
    $skus = Get-MgSubscribedSku -All
    $copilotSkus = @('Microsoft_365_Copilot')
    $assigned = $skus | Where-Object { $copilotSkus -contains $_.SkuPartNumber -and $_.ConsumedUnits -gt 0 }
    if (-not $assigned) {
        $issues += [pscustomobject]@{ Severity='Blocker'; Gate='License';      Detail='No assigned Microsoft 365 Copilot SKU detected.' }
    }

    # RBAC: Compliance Administrator
    $me = Get-MgContext
    $roleAssignments = Get-MgRoleManagementDirectoryRoleAssignment -Filter "principalId eq '$($me.ClientId)'" -ErrorAction SilentlyContinue
    $hasCompliance = $roleAssignments | ForEach-Object {
        (Get-MgRoleManagementDirectoryRoleDefinition -UnifiedRoleDefinitionId $_.RoleDefinitionId).DisplayName
    } | Where-Object { $_ -in @('Compliance Administrator','Compliance Data Administrator','Global Administrator') }
    if (-not $hasCompliance) {
        $issues += [pscustomobject]@{ Severity='Blocker'; Gate='RBAC-Compliance'; Detail='Caller lacks Compliance Administrator (or higher).' }
    }

    # RBAC: SharePoint Administrator (probe with low-impact call)
    try { $null = Get-SPOTenant -ErrorAction Stop }
    catch { $issues += [pscustomobject]@{ Severity='Blocker'; Gate='RBAC-SharePoint'; Detail="Get-SPOTenant failed: $($_.Exception.Message)" } }

    # Cmdlet surface: RSS
    $spoCmd = Get-Command Set-SPOTenant -ErrorAction Stop
    $hasRssParam = $spoCmd.Parameters.ContainsKey('RestrictedSearchApplicableToAllSites')
    $hasLegacyRss = (Get-Command Set-SPOTenantRestrictedSearchMode -ErrorAction SilentlyContinue) -ne $null
    if (-not $hasRssParam -and -not $hasLegacyRss) {
        $issues += [pscustomobject]@{ Severity='Blocker'; Gate='RSS-Cmdlets'; Detail='Neither Set-SPOTenant -RestrictedSearchApplicableToAllSites nor Set-SPOTenantRestrictedSearchMode are present. Update Microsoft.Online.SharePoint.PowerShell.' }
    }

    # Cmdlet surface: DLP for Copilot workload
    $dlpCmd = Get-Command New-DlpComplianceRule -ErrorAction Stop
    $workloadValues = ($dlpCmd.Parameters['Workload'].Attributes |
                       Where-Object { $_ -is [System.Management.Automation.ValidateSetAttribute] }).ValidValues
    if ('MicrosoftCopilotExperience' -notin $workloadValues) {
        $issues += [pscustomobject]@{ Severity='Blocker'; Gate='DLP-Workload'; Detail='New-DlpComplianceRule does not accept -Workload MicrosoftCopilotExperience. Update ExchangeOnlineManagement to 3.5 or later.' }
    }

    # Multi-geo posture (warn only)
    try {
        $mg = Get-SPOMultiGeoExperience -ErrorAction Stop
        if ($mg) { Write-Verbose "Multi-geo enabled in $($Session.Cloud)." }
    } catch {
        $issues += [pscustomobject]@{ Severity='Warning'; Gate='MultiGeo'; Detail='Multi-geo probe failed; verify scope manually.' }
    }

    Write-Agt47Evidence -Session $Session -Stage 'preflight' -Payload @{
        Issues = $issues
        Skus   = $assigned | Select-Object SkuPartNumber, ConsumedUnits, PrepaidUnits
    }

    $blocker = $issues | Where-Object Severity -eq 'Blocker'
    if ($blocker) {
        $blocker | Format-Table | Out-String | Write-Error
        exit 2
    }
    if ($issues) { return 1 } else { return 0 }
}
```

The `Write-Agt47Evidence` helper used throughout this playbook is defined in §10. It writes a JSON payload, computes its SHA-256, appends to a session manifest, and updates a hash-of-hashes manifest digest.

---

## 4. Sensitivity label policy: `Set-Agt47LabelPolicy`

Sensitivity labels are the cornerstone of Copilot grounding governance. Labels drive which content Copilot can summarize, paraphrase, and cite, which content is excluded from grounding via DLP rules (§5), and which content is excluded from search index expansion via RSS (§6). FSI tenants typically operate four labels: `Public`, `Internal`, `Confidential`, and `Highly Confidential\NPI` (or `MNPI`). The label structure is created through Control 1.5 (Data Loss Prevention (DLP) and Sensitivity Labels). This control consumes that label taxonomy and configures the **policy** that publishes labels to Copilot-licensed users.

The mutation pattern follows [BL-§3](../../_shared/powershell-baseline.md#3-mutation-safety-supportsshouldprocess-whatif-snapshot):

1. Bootstrap session (§2)
2. Pre-flight gates (§3)
3. **Before-snapshot** of `Get-LabelPolicy` and `Get-Label` to JSON
4. `Set-LabelPolicy` with `-WhatIf` rehearsal
5. Apply with `-Confirm:$false` only when `-Force` is explicitly passed
6. **After-snapshot** and field-level diff
7. Emit evidence

```powershell
function Set-Agt47LabelPolicy {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] $Session,
        [Parameter(Mandatory)] [string] $PolicyName,
        [Parameter(Mandatory)] [string[]] $Labels,
        [Parameter(Mandatory)] [string[]] $ScopeUserGroups,
        [string] $DefaultLabel = 'Internal',
        [switch] $Force
    )

    if (-not $Session) { Write-Error "Run Initialize-Agt47Session first."; exit 2 }

    $beforeLabels   = Get-Label   | Select-Object Name, DisplayName, Priority, ContentType, ParentId
    $beforePolicies = Get-LabelPolicy | Select-Object Name, Labels, Settings, ScopedLabels, Mode, ExchangeLocation
    $before = @{ Labels = $beforeLabels; Policies = $beforePolicies }
    Write-Agt47Evidence -Session $Session -Stage 'labels-before' -Payload $before

    $missing = $Labels | Where-Object { $_ -notin $beforeLabels.Name }
    if ($missing) {
        Write-Error "Agt47: Labels not present in tenant: $($missing -join ', '). Create them via Control 4.6 first."
        exit 2
    }

    $existing = Get-LabelPolicy -Identity $PolicyName -ErrorAction SilentlyContinue
    if (-not $existing) {
        if ($PSCmdlet.ShouldProcess($PolicyName,'New-LabelPolicy')) {
            New-LabelPolicy -Name $PolicyName -Labels $Labels -ExchangeLocation 'All' | Out-Null
        }
    } else {
        if ($PSCmdlet.ShouldProcess($PolicyName,'Set-LabelPolicy (label set)')) {
            Set-LabelPolicy -Identity $PolicyName -AddLabels $Labels -ErrorAction Stop
        }
    }

    $advancedSettings = @{
        DefaultLabelId                     = (Get-Label -Identity $DefaultLabel).ImmutableId.ToString()
        EnableLabelByDefault               = 'true'
        RequireDowngradeJustification      = 'true'
        EnableMandatoryInOutlook           = 'true'
        EnableSensitiveServicesPanel       = 'true'
    }
    foreach ($k in $advancedSettings.Keys) {
        if ($PSCmdlet.ShouldProcess($PolicyName,"Set-LabelPolicy AdvancedSettings $k")) {
            Set-LabelPolicy -Identity $PolicyName -AdvancedSettings @{ $k = $advancedSettings[$k] }
        }
    }

    foreach ($g in $ScopeUserGroups) {
        if ($PSCmdlet.ShouldProcess($PolicyName,"Add scope group $g")) {
            Set-LabelPolicy -Identity $PolicyName -AddLabelPolicyLocationException @{ Identity=$g } -ErrorAction SilentlyContinue
        }
    }

    $afterPolicy = Get-LabelPolicy -Identity $PolicyName | Select-Object *
    Write-Agt47Evidence -Session $Session -Stage 'labels-after' -Payload @{ Policy = $afterPolicy }

    $verifyDefault = ($afterPolicy.Settings | Where-Object Key -eq 'DefaultLabelId').Value
    if (-not $verifyDefault) {
        Write-Error "Agt47: DefaultLabelId did not persist on policy $PolicyName. Investigate before re-running."
        exit 2
    }

    Write-Host "Agt47: Label policy '$PolicyName' applied. Default label = $DefaultLabel."
}
```

**FSI guidance.**

- Apply this policy to the same Entra security group that holds Copilot license assignments (Control 2.1). Drift between license and label-policy scope is the most common cause of "Copilot summarized content the user could not normally read".
- `RequireDowngradeJustification = true` provides a justification audit trail under FINRA 3110 supervision and OCC Bulletin 2026-13 (formerly OCC 2011-12) model risk reviews.
- `MNPI` / `NPI` labels must always carry encryption (configured under Control 4.6) so that Copilot prompt and response surfaces honor cipher boundaries even when DLP §5 is misconfigured.

---

## 5. DLP for Copilot: `Set-Agt47CopilotDlp`

DLP for Copilot ships under the **`MicrosoftCopilotExperience`** workload in `New-DlpComplianceRule`. It exposes two distinct rule shapes that **must not be combined** in a single rule:

- **Prompt-side restriction** (`PromptContains` action): blocks user prompts that contain sensitive information types (SITs) — for example, blocking a prompt that pastes a Social Security Number into Copilot Chat.
- **Grounding-side restriction** (`ContentContainsSensitiveInformation` / sensitivity label match): excludes labeled SharePoint, OneDrive, and Loop content from being grounded in Copilot responses.

Combining both shapes in one rule causes the rule to silently no-op against grounding sources because the SIT match does not apply to grounding content. **Always create two rules under one policy.**

```powershell
function Set-Agt47CopilotDlp {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] $Session,
        [Parameter(Mandatory)] [string] $PolicyName,
        [Parameter(Mandatory)] [string[]] $RestrictedSitNames,
        [Parameter(Mandatory)] [string[]] $RestrictedLabelGuids,
        [string] $PromptRuleName    = "$PolicyName - Prompt SIT block",
        [string] $GroundingRuleName = "$PolicyName - Grounding label exclusion",
        [switch] $Force
    )
    if (-not $Session) { Write-Error "Run Initialize-Agt47Session first."; exit 2 }

    $beforePolicy = Get-DlpCompliancePolicy -Identity $PolicyName -ErrorAction SilentlyContinue
    $beforeRules  = if ($beforePolicy) { Get-DlpComplianceRule -Policy $PolicyName } else { @() }
    Write-Agt47Evidence -Session $Session -Stage 'dlp-before' -Payload @{ Policy=$beforePolicy; Rules=$beforeRules }

    if (-not $beforePolicy) {
        if ($PSCmdlet.ShouldProcess($PolicyName,'New-DlpCompliancePolicy')) {
            New-DlpCompliancePolicy `
                -Name $PolicyName `
                -Mode Enable `
                -Comment 'Agt47 - Copilot prompt and grounding governance' `
                -ExchangeLocation 'All' `
                -SharePointLocation 'All' `
                -OneDriveLocation 'All' | Out-Null
        }
    } else {
        Set-DlpCompliancePolicy -Identity $PolicyName -Mode Enable | Out-Null
    }

    # Rule A: Prompt-side SIT block (workload = MicrosoftCopilotExperience, action = block prompt)
    $sitBlock = $RestrictedSitNames | ForEach-Object {
        @{ Name = $_; minCount = 1; confidencelevel = 'High' }
    }
    $promptRuleParams = @{
        Name                                  = $PromptRuleName
        Policy                                = $PolicyName
        Workload                              = 'MicrosoftCopilotExperience'
        ContentContainsSensitiveInformation   = $sitBlock
        BlockAccess                           = $true
        BlockAccessScope                      = 'PerUser'
        NotifyUser                            = 'SiteAdmin','LastModifier','Owner'
        NotifyUserType                        = 'NotSet'
        GenerateAlert                         = $true
    }
    if ($PSCmdlet.ShouldProcess($PromptRuleName,'New-DlpComplianceRule (prompt block)')) {
        if (Get-DlpComplianceRule -Identity $PromptRuleName -ErrorAction SilentlyContinue) {
            Set-DlpComplianceRule -Identity $PromptRuleName @promptRuleParams | Out-Null
        } else {
            New-DlpComplianceRule @promptRuleParams | Out-Null
        }
    }

    # Rule B: Grounding-side label exclusion (workload = MicrosoftCopilotExperience, action = exclude from grounding)
    $labelMatch = $RestrictedLabelGuids | ForEach-Object {
        @{ operator='And'; groups = @( @{ operator='Or'; labels = @( @{ name = $_ } ) } ) }
    }
    $groundingRuleParams = @{
        Name                          = $GroundingRuleName
        Policy                        = $PolicyName
        Workload                      = 'MicrosoftCopilotExperience'
        ContentContainsSensitiveInformation = $labelMatch
        BlockAccess                   = $true
        BlockAccessScope              = 'PerUser'
        NotifyUser                    = 'SiteAdmin','LastModifier','Owner'
        GenerateAlert                 = $true
    }
    if ($PSCmdlet.ShouldProcess($GroundingRuleName,'New-DlpComplianceRule (grounding exclusion)')) {
        if (Get-DlpComplianceRule -Identity $GroundingRuleName -ErrorAction SilentlyContinue) {
            Set-DlpComplianceRule -Identity $GroundingRuleName @groundingRuleParams | Out-Null
        } else {
            New-DlpComplianceRule @groundingRuleParams | Out-Null
        }
    }

    $afterPolicy = Get-DlpCompliancePolicy -Identity $PolicyName
    $afterRules  = Get-DlpComplianceRule  -Policy   $PolicyName | Select-Object Name, Workload, Mode, Disabled, BlockAccess, BlockAccessScope, ContentContainsSensitiveInformation
    Write-Agt47Evidence -Session $Session -Stage 'dlp-after' -Payload @{ Policy=$afterPolicy; Rules=$afterRules }

    $bad = $afterRules | Where-Object { $_.Workload -ne 'MicrosoftCopilotExperience' -or $_.Disabled }
    if ($bad) {
        $bad | Format-Table | Out-String | Write-Error
        Write-Error "Agt47: Copilot DLP rules disabled or wrong workload. Fail-closed."
        exit 2
    }
    Write-Host "Agt47: DLP policy '$PolicyName' enforced (prompt + grounding rules)."
}
```

**FSI guidance.**

- The prompt-block rule **does not** prevent a user from seeing labeled content in SharePoint — it only blocks Copilot from grounding on it and from accepting prompts that contain selected SITs. Use this rule to enforce SEC Reg S-P customer-information protections inside Copilot prompts.
- For MNPI/NPI grounding exclusion, set `BlockAccessScope = 'PerUser'`, not `'All'`. `'All'` blocks anonymous web crawlers as well, which has no effect on Copilot but generates noisy alerts.
- Set `GenerateAlert = $true` so violations land in Defender XDR for SOC review under Control 1.12 (Insider Risk Detection and Response).
- Audit Copilot prompt and response activity via `UnifiedAuditLog` (record types `CopilotInteraction`, `CopilotEvent`); Control 1.7 (Comprehensive Audit Logging and Compliance) covers the export pipeline.

---

## 6. Restricted SharePoint Search: `Set-Agt47RestrictedSearch`

Restricted SharePoint Search (RSS) constrains organization-wide search and Copilot grounding to an admin-curated allow-list of SharePoint sites. RSS is the **primary mitigation for "oversharing-via-Copilot"**: if a SharePoint site is permission-misconfigured, RSS prevents Copilot from grounding on it until a Site Lifecycle review (Control 4.4) clears it for inclusion.

The cmdlet surface evolved during 2025-2026. The function below **probes the surface first** and prefers the modern parameter; it falls back to the legacy mode cmdlet if the modern parameter is absent and **fails closed** if neither is present.

```powershell
function Set-Agt47RestrictedSearch {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] $Session,
        [Parameter(Mandatory)] [string[]] $AllowedSiteUrls,
        [switch] $Force
    )
    if (-not $Session) { Write-Error "Run Initialize-Agt47Session first."; exit 2 }

    $beforeTenant   = Get-SPOTenant
    $beforeAllowed  = try { Get-SPOTenantRestrictedSearchAllowedList -ErrorAction Stop } catch { @() }
    Write-Agt47Evidence -Session $Session -Stage 'rss-before' -Payload @{
        Tenant  = $beforeTenant | Select-Object RestrictedSearchApplicableToAllSites, RestrictedSearchMode, SearchResolveExactEmailOrUPN
        Allowed = $beforeAllowed
    }

    $spoCmd       = Get-Command Set-SPOTenant
    $hasModern    = $spoCmd.Parameters.ContainsKey('RestrictedSearchApplicableToAllSites')
    $legacyExists = (Get-Command Set-SPOTenantRestrictedSearchMode -ErrorAction SilentlyContinue) -ne $null

    if ($hasModern) {
        if ($PSCmdlet.ShouldProcess('Tenant','Set-SPOTenant -RestrictedSearchApplicableToAllSites $true')) {
            Set-SPOTenant -RestrictedSearchApplicableToAllSites $true | Out-Null
        }
    } elseif ($legacyExists) {
        Write-Warning "Modern -RestrictedSearchApplicableToAllSites not present; falling back to Set-SPOTenantRestrictedSearchMode -Mode Enabled. Plan to update Microsoft.Online.SharePoint.PowerShell."
        if ($PSCmdlet.ShouldProcess('Tenant','Set-SPOTenantRestrictedSearchMode -Mode Enabled')) {
            Set-SPOTenantRestrictedSearchMode -Mode Enabled | Out-Null
        }
    } else {
        Write-Error "Agt47: Neither modern nor legacy RSS cmdlet surface present. Fail-closed."
        exit 2
    }

    foreach ($u in $AllowedSiteUrls) {
        if ($u -notmatch '^https?://') {
            Write-Error "Agt47: $u is not a fully-qualified site URL."; exit 2
        }
        if ($PSCmdlet.ShouldProcess($u,'Add-SPOTenantRestrictedSearchAllowedList')) {
            try {
                Add-SPOTenantRestrictedSearchAllowedList -SitesList @($u) -ErrorAction Stop | Out-Null
            } catch {
                if ($_.Exception.Message -match 'already') { Write-Verbose "Already in list: $u" }
                else { throw }
            }
        }
    }

    Start-Sleep -Seconds 30  # tenant cache warm-up

    $afterTenant  = Get-SPOTenant
    $afterAllowed = Get-SPOTenantRestrictedSearchAllowedList
    Write-Agt47Evidence -Session $Session -Stage 'rss-after' -Payload @{
        Tenant  = $afterTenant | Select-Object RestrictedSearchApplicableToAllSites, RestrictedSearchMode, SearchResolveExactEmailOrUPN
        Allowed = $afterAllowed
    }

    $isOn = $afterTenant.RestrictedSearchApplicableToAllSites -eq $true -or $afterTenant.RestrictedSearchMode -eq 'Enabled'
    if (-not $isOn) {
        Write-Error "Agt47: RSS did not enable. Investigate before re-running."
        exit 2
    }
    $missing = $AllowedSiteUrls | Where-Object { $_ -notin ($afterAllowed.SiteUrl) -and $_ -notin $afterAllowed }
    if ($missing) {
        Write-Warning "Agt47: Allowed-list entries not yet visible (eventual consistency, may take up to 24h): $($missing -join ', ')"
    }
    Write-Host "Agt47: Restricted SharePoint Search enforced; $($AllowedSiteUrls.Count) site(s) submitted to allow-list."
}
```

**FSI guidance.**

- RSS is **enabled per tenant**, not per site. Once on, only sites in the allow-list participate in org-wide search and Copilot grounding. Site Lifecycle (Control 4.4) is the gate that promotes a site from "RSS-restricted" to "Copilot-grounded".
- The allow-list propagates eventually (up to 24 hours). Validation (§10) will warn (exit 1) on stale state and re-run on next pass.
- For broker-dealers, RSS gives a defensible answer to FINRA 3110 supervisory questions: "Which sites can Copilot ground on?" The allow-list **is** the answer.
- RSS does not replace SharePoint permission hygiene. It complements it. Use Control 4.5 (DAG Reviews) to keep the allow-listed sites tightly permissioned.

---

## 7. Endpoint DLP for Copilot: `Set-Agt47EndpointDlp`

Endpoint DLP for Copilot prevents the **client-side leak path**: a user copies sensitive content from a labeled document and pastes it into Microsoft 365 Copilot Chat (Web), Copilot in Edge, or a third-party Copilot surface. Without endpoint DLP, the prompt-side rule from §5 only catches matches against the configured SIT list; freeform prose containing client identifiers can slip through.

```powershell
function Set-Agt47EndpointDlp {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] $Session,
        [Parameter(Mandatory)] [string] $PolicyName,
        [Parameter(Mandatory)] [string[]] $RestrictedSitNames,
        [string] $RuleName = "$PolicyName - pasteToCopilot block",
        [string[]] $AllowedBrowsers = @('msedge.exe','chrome.exe'),  # Edge required for full enforcement
        [switch] $Force
    )
    if (-not $Session) { Write-Error "Run Initialize-Agt47Session first."; exit 2 }

    if ('msedge.exe' -notin $AllowedBrowsers) {
        Write-Error "Agt47: Microsoft Edge is required in AllowedBrowsers for endpoint pasteToCopilot enforcement on Copilot for Web. Fail-closed."
        exit 2
    }

    $beforePolicy = Get-DlpCompliancePolicy -Identity $PolicyName -ErrorAction SilentlyContinue
    Write-Agt47Evidence -Session $Session -Stage 'edlp-before' -Payload @{ Policy = $beforePolicy }

    if (-not $beforePolicy) {
        if ($PSCmdlet.ShouldProcess($PolicyName,'New-DlpCompliancePolicy (endpoint)')) {
            New-DlpCompliancePolicy `
                -Name $PolicyName `
                -Mode Enable `
                -Comment 'Agt47 - Endpoint DLP for Copilot pasteToCopilot' `
                -EndpointDlpLocation 'All' | Out-Null
        }
    }

    $sit = $RestrictedSitNames | ForEach-Object { @{ Name=$_; minCount=1; confidencelevel='High' } }

    $endpointActions = @(
        @{ EndpointDlpRestrictionAction='Block'; EndpointDlpRestrictionType='pasteToBrowserSupportedSites' }
        @{ EndpointDlpRestrictionAction='Block'; EndpointDlpRestrictionType='pasteToCopilot' }
        @{ EndpointDlpRestrictionAction='Block'; EndpointDlpRestrictionType='copyToClipboard' }
    )

    $params = @{
        Name                                 = $RuleName
        Policy                               = $PolicyName
        ContentContainsSensitiveInformation  = $sit
        BlockAccess                          = $true
        EndpointDlpRestrictions              = $endpointActions
        EndpointDlpBrowserRestrictions       = @{ AllowedBrowsers = $AllowedBrowsers }
        GenerateAlert                        = $true
        NotifyUser                           = 'LastModifier'
    }
    if ($PSCmdlet.ShouldProcess($RuleName,'New-DlpComplianceRule (endpoint)')) {
        if (Get-DlpComplianceRule -Identity $RuleName -ErrorAction SilentlyContinue) {
            Set-DlpComplianceRule -Identity $RuleName @params | Out-Null
        } else {
            New-DlpComplianceRule @params | Out-Null
        }
    }

    $afterRule = Get-DlpComplianceRule -Identity $RuleName | Select-Object Name, Disabled, EndpointDlpRestrictions, EndpointDlpBrowserRestrictions
    Write-Agt47Evidence -Session $Session -Stage 'edlp-after' -Payload @{ Rule=$afterRule }

    $hasPaste = $afterRule.EndpointDlpRestrictions | Where-Object { $_.EndpointDlpRestrictionType -eq 'pasteToCopilot' -and $_.EndpointDlpRestrictionAction -eq 'Block' }
    if (-not $hasPaste) {
        Write-Error "Agt47: pasteToCopilot block did not persist on rule $RuleName. Fail-closed."
        exit 2
    }
    Write-Host "Agt47: Endpoint DLP rule '$RuleName' enforces pasteToCopilot block."
}
```

**FSI guidance.**

- Endpoint DLP requires Microsoft Defender for Endpoint onboarding (Control 1.10). On non-onboarded devices the rule **silently does nothing** — verify device coverage via `Get-MgDeviceManagementManagedDevice` before claiming coverage.
- Edge is the only browser that surfaces the `pasteToCopilot` restriction natively for Copilot for Web. Other browsers (Chrome, Firefox) inherit `pasteToBrowserSupportedSites` only; mixed-browser environments will see partial enforcement.
- Endpoint DLP applies only to **managed devices** (Intune-enrolled or Defender-onboarded). BYOD via Azure Virtual Desktop or Windows 365 inherits enforcement only when the host is managed.

---

## 8. Copilot Pages and Notebooks retention: `Set-Agt47CopilotRetention`

Copilot Pages and Copilot Notebooks are stored in **SharePoint Embedded** containers, **not** in the user's OneDrive or in a SharePoint document library. This has three consequences for FSI retention:

1. The standard SharePoint and OneDrive retention policies **do not apply automatically** to Copilot Pages and Notebooks. A separate Microsoft Purview retention policy targeting `CopilotInteractions` (and where applicable, Copilot Pages containers) must be configured.
2. Copilot Notebooks **do not have a recycle bin** in the user-facing UI. Once a user "deletes" a notebook, recovery requires admin intervention against the SharePoint Embedded container — within the retention window only.
3. **Manual hold** (eDiscovery preservation hold) on Copilot containers is a separate operation; legal hold under Control 1.19 (eDiscovery for Agent Interactions) must explicitly target the Copilot Pages container set.

```powershell
function Set-Agt47CopilotRetention {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] $Session,
        [Parameter(Mandatory)] [string] $PolicyName,
        [Parameter(Mandatory)] [int]    $RetentionYears = 7,
        [Parameter(Mandatory)] [ValidateSet('Retain','RetainAndDelete')] [string] $Action = 'RetainAndDelete'
    )
    if (-not $Session) { Write-Error "Run Initialize-Agt47Session first."; exit 2 }

    $beforePolicy = Get-RetentionCompliancePolicy -Identity $PolicyName -ErrorAction SilentlyContinue
    Write-Agt47Evidence -Session $Session -Stage 'retention-before' -Payload @{ Policy = $beforePolicy }

    $retainDays = $RetentionYears * 365

    if (-not $beforePolicy) {
        if ($PSCmdlet.ShouldProcess($PolicyName,'New-RetentionCompliancePolicy (Copilot)')) {
            New-RetentionCompliancePolicy `
                -Name $PolicyName `
                -TeamsChatLocation 'All' `
                -ModernGroupLocation 'All' `
                -Comment "Agt47 - Copilot interaction retention $RetentionYears years" | Out-Null
        }
    }

    $ruleName = "$PolicyName - rule"
    $ruleParams = @{
        Name                            = $ruleName
        Policy                          = $PolicyName
        RetentionDuration               = $retainDays
        RetentionComplianceAction       = $Action
        ApplyComplianceTag              = $null
        ContentMatchQuery               = $null
        ExpirationDateOption            = 'CreationAgeInDays'
    }
    if ($PSCmdlet.ShouldProcess($ruleName,'New/Set-RetentionComplianceRule')) {
        if (Get-RetentionComplianceRule -Identity $ruleName -ErrorAction SilentlyContinue) {
            Set-RetentionComplianceRule -Identity $ruleName @ruleParams | Out-Null
        } else {
            New-RetentionComplianceRule @ruleParams | Out-Null
        }
    }

    $afterPolicy = Get-RetentionCompliancePolicy -Identity $PolicyName
    $afterRule   = Get-RetentionComplianceRule   -Identity $ruleName | Select-Object Name, RetentionDuration, RetentionComplianceAction
    Write-Agt47Evidence -Session $Session -Stage 'retention-after' -Payload @{ Policy=$afterPolicy; Rule=$afterRule }

    if ($afterRule.RetentionDuration -ne $retainDays) {
        Write-Error "Agt47: Retention duration mismatch on $ruleName. Expected $retainDays days, got $($afterRule.RetentionDuration). Fail-closed."
        exit 2
    }
    Write-Host "Agt47: Copilot retention policy '$PolicyName' applied: $RetentionYears years, action=$Action."
}
```

**FSI guidance.**

- For SEC 17a-4(f) immutability, set `RetentionComplianceAction = 'RetainAndDelete'` and combine with **Preservation Lock** (Control 1.7) so the policy itself cannot be shortened or deleted. Without preservation lock, an administrator can reduce retention and you lose immutability.
- 7 years aligns with FINRA 4511 default; 6 years is the SEC 17a-4(b) minimum for most records. Prefer the longer of the two unless legal explicitly approves a shorter window.
- Copilot Pages **content** (the rich-text page itself) is captured by the SharePoint Embedded retention policy; Copilot Pages **chat sidebar interactions** are captured by the `TeamsChatLocation` scope above.
- Manual hold via `New-CaseHoldPolicy` against the Copilot container set is a Control 1.19 procedure; it overrides this policy for legal hold scope only.
- Document the retention design in your WORM/SEC 17a-4 evidence pack alongside Control 1.7 (Comprehensive Audit Logging and Compliance).

---

## 9. Multi-geo grounding scope: `Test-Agt47MultiGeoScope`

In multi-geo tenants Copilot grounding respects the **user's preferred data location (PDL)**. A user in the EU geo can ground only on content stored in their EU geo unless cross-geo search is explicitly enabled. The function below inventories the geo configuration and flags any cross-geo expansion that has been turned on without an explicit FSI risk acceptance.

```powershell
function Test-Agt47MultiGeoScope {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $Session
    )
    if (-not $Session) { Write-Error "Run Initialize-Agt47Session first."; exit 2 }

    $issues = @()
    try {
        $mg = Get-SPOMultiGeoExperience -ErrorAction Stop
    } catch {
        Write-Verbose "Multi-geo not enabled in $($Session.Cloud); skipping."
        Write-Agt47Evidence -Session $Session -Stage 'multigeo' -Payload @{ Enabled=$false }
        return 0
    }

    $geoLocations = Get-SPOGeoStorageQuota -ErrorAction Stop
    $crossGeo     = Get-SPOCrossGeoMovedUsers -ErrorAction SilentlyContinue
    $tenant       = Get-SPOTenant
    $crossGeoSearch = $tenant.SearchResolveExactEmailOrUPN

    foreach ($g in $geoLocations) {
        if ($g.GeoLocation -in @('EUR','GBR','CHE','NOR','FRA','DEU')) {
            if ($crossGeoSearch) {
                $issues += [pscustomobject]@{ Severity='Warning'; Geo=$g.GeoLocation; Detail='Cross-geo search resolution enabled; verify Anthropic subprocessor and EU Data Boundary posture.' }
            }
        }
    }

    Write-Agt47Evidence -Session $Session -Stage 'multigeo' -Payload @{
        Enabled         = $true
        Geos            = $geoLocations
        CrossGeoMoved   = $crossGeo
        CrossGeoSearch  = $crossGeoSearch
        Issues          = $issues
    }
    if ($issues) { return 1 } else { return 0 }
}
```

**FSI guidance.**

- For tenants with an EU/EFTA/UK footprint, confirm that the **Anthropic Claude subprocessor is disabled by default** and that no admin override has flipped it on for a Researcher or Copilot Studio scenario. Anthropic processing is **outside the EU Data Boundary**.
- For US-only tenants in Commercial cloud, Anthropic is **enabled by default** for selected scenarios; document this in your Vendor & Subprocessor inventory under Control 2.7 and the Procurement Diligence pack (Control 2.10).

---

## 10. Validation: `Test-Agt47Implementation` / `Test-Agt47Compliance` and evidence emission

This section defines the read-only validator and the evidence helper. Both are **fail-closed** with exit codes:

- **0** — Clean. All required policies present and enforcing.
- **1** — Warnings. Non-blocking findings (e.g., RSS allow-list propagation lag, multi-geo posture warnings).
- **2** — Blocker. A required policy is missing, in the wrong workload, disabled, or the cmdlet surface is stale.

```powershell
function Write-Agt47Evidence {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $Session,
        [Parameter(Mandatory)] [string] $Stage,
        [Parameter(Mandatory)] [hashtable] $Payload
    )
    $ts   = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    $file = Join-Path $Session.SessionDir "$Stage-$ts.json"

    $envelope = [pscustomobject]@{
        RunId        = $Session.RunId
        Cloud        = $Session.Cloud
        TenantId     = $Session.TenantId
        Stage        = $Stage
        CapturedAtUtc= $ts
        Payload      = $Payload
    }
    $json = $envelope | ConvertTo-Json -Depth 12
    Set-Content -LiteralPath $file -Value $json -Encoding utf8

    $sha = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash
    "$sha  $(Split-Path $file -Leaf)" | Add-Content -LiteralPath (Join-Path $Session.SessionDir 'manifest.sha256')

    $manifestPath = Join-Path $Session.SessionDir 'manifest.json'
    $manifest = if (Test-Path $manifestPath) { Get-Content $manifestPath -Raw | ConvertFrom-Json } else {
        [pscustomobject]@{ RunId=$Session.RunId; Files=@(); Digest=$null }
    }
    $manifest.Files += [pscustomobject]@{ Stage=$Stage; File=(Split-Path $file -Leaf); Sha256=$sha; CapturedAtUtc=$ts }
    $hashOfHashes = ($manifest.Files | ForEach-Object { $_.Sha256 }) -join '|'
    $digestBytes  = [System.Text.Encoding]::UTF8.GetBytes($hashOfHashes)
    $manifest.Digest = [System.BitConverter]::ToString(
        [System.Security.Cryptography.SHA256]::Create().ComputeHash($digestBytes)
    ).Replace('-','')
    $manifest | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $manifestPath -Encoding utf8
}

function Test-Agt47Implementation {
    [CmdletBinding()]
    param([Parameter(Mandatory)] $Session)
    if (-not $Session) { Write-Error "Run Initialize-Agt47Session first."; exit 2 }

    $findings = New-Object System.Collections.Generic.List[object]
    function Add-F([string]$Severity,[string]$Area,[string]$Detail) {
        $findings.Add([pscustomobject]@{ Severity=$Severity; Area=$Area; Detail=$Detail })
    }

    # Labels
    $labelPolicies = Get-LabelPolicy
    if (-not $labelPolicies) { Add-F 'Blocker' 'Labels' 'No label policies present.' }

    # DLP for Copilot
    $dlpRules = Get-DlpComplianceRule
    $copilotRules = $dlpRules | Where-Object { $_.Workload -eq 'MicrosoftCopilotExperience' -and -not $_.Disabled }
    if (-not $copilotRules) {
        Add-F 'Blocker' 'DLP-Copilot' 'No enforcing DLP rule found with Workload = MicrosoftCopilotExperience.'
    } else {
        $promptish    = $copilotRules | Where-Object { $_.ContentContainsSensitiveInformation -and -not ($_.ContentContainsSensitiveInformation.groups) }
        $groundingish = $copilotRules | Where-Object { $_.ContentContainsSensitiveInformation.groups }
        if (-not $promptish)    { Add-F 'Warning' 'DLP-Copilot' 'No prompt-side SIT rule detected.' }
        if (-not $groundingish) { Add-F 'Warning' 'DLP-Copilot' 'No grounding-side label-exclusion rule detected.' }
    }

    # RSS
    $tenant = Get-SPOTenant
    $rssOn  = $tenant.RestrictedSearchApplicableToAllSites -eq $true -or $tenant.RestrictedSearchMode -eq 'Enabled'
    if (-not $rssOn) { Add-F 'Blocker' 'RSS' 'Restricted SharePoint Search is not enabled.' }
    $allow = try { Get-SPOTenantRestrictedSearchAllowedList -ErrorAction Stop } catch { @() }
    if ($rssOn -and -not $allow) { Add-F 'Warning' 'RSS' 'RSS enabled but allow-list is empty.' }

    # Endpoint DLP
    $edlp = $dlpRules | Where-Object { $_.EndpointDlpRestrictions.EndpointDlpRestrictionType -contains 'pasteToCopilot' -and -not $_.Disabled }
    if (-not $edlp) { Add-F 'Warning' 'Endpoint-DLP' 'No enforcing endpoint DLP rule blocks pasteToCopilot.' }

    # Retention
    $retention = Get-RetentionCompliancePolicy | Where-Object { $_.TeamsChatLocation }
    if (-not $retention) { Add-F 'Blocker' 'Retention' 'No retention policy targets Copilot interactions (TeamsChatLocation).' }

    Write-Agt47Evidence -Session $Session -Stage 'validate' -Payload @{ Findings=$findings }

    $blockers = $findings | Where-Object Severity -eq 'Blocker'
    $warnings = $findings | Where-Object Severity -eq 'Warning'
    $findings | Format-Table -AutoSize | Out-String | Write-Host
    if ($blockers.Count -gt 0) { return 2 }
    if ($warnings.Count -gt 0) { return 1 }
    return 0
}

# Convenience alias
Set-Alias -Name Test-Agt47Compliance -Value Test-Agt47Implementation -Scope Global
```

`Invoke-Agt47Verification` is the suggested wrapper that runs the full sequence end-to-end:

```powershell
function Invoke-Agt47Verification {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $TenantId,
        [Parameter(Mandatory)] [string] $TenantDomainPrefix,
        [Parameter(Mandatory)] [string] $EvidenceRoot
    )
    $session = Initialize-Agt47Session -TenantId $TenantId -TenantDomainPrefix $TenantDomainPrefix -EvidenceRoot $EvidenceRoot
    $script:Agt47Session = $session
    $pf = Test-Agt47Prerequisites -Session $session
    if ($pf -eq 2) { exit 2 }
    $rc = Test-Agt47Implementation -Session $session
    Write-Host "Agt47 verification exit code: $rc (manifest: $(Join-Path $session.SessionDir 'manifest.json'))"
    exit $rc
}
```

**Evidence output structure.**

```
agt47-<RunId>/
  session.json
  preflight-<ts>.json
  labels-before-<ts>.json
  labels-after-<ts>.json
  dlp-before-<ts>.json
  dlp-after-<ts>.json
  rss-before-<ts>.json
  rss-after-<ts>.json
  edlp-before-<ts>.json
  edlp-after-<ts>.json
  retention-before-<ts>.json
  retention-after-<ts>.json
  multigeo-<ts>.json
  validate-<ts>.json
  manifest.json         # per-file SHA-256 + hash-of-hashes digest
  manifest.sha256       # POSIX-style sha256sum file
```

The `Digest` field in `manifest.json` is the SHA-256 of the pipe-joined per-file hashes, which provides a single value to attest to the integrity of the entire run for FINRA 4511 / SEC 17a-4 records reproducibility.

---

## 11. Anti-patterns

The 18 anti-patterns below are the false-clean and silent-failure modes most often observed in FSI Copilot governance engagements. Each names the symptom, the root cause, and the §-anchored remediation.

| # | Anti-pattern | Why it fails | Remediation |
|---|---|---|---|
| 1 | Running the playbook in Windows PowerShell 5.1 | PnP v2 and ExchangeOnlineManagement v3+ silently mis-bind; cmdlet probes return false negatives | §0 shell guard; refuse to run if not 7.4 Core |
| 2 | Floating module versions (`Install-Module -Force` with no `-RequiredVersion`) | Reproducibility broken; FINRA 4511 / SEC 17a-4 evidence weakened | §1 pinned `-RequiredVersion` |
| 3 | Combining prompt-SIT and grounding-label match in one DLP rule | Grounding rule silently no-ops; "all green" with zero enforcement | §5 split into two rules under one policy |
| 4 | DLP rule using `-Workload SharePoint` instead of `MicrosoftCopilotExperience` | Rule applies to SharePoint surfaces only; Copilot grounding bypasses it | §5 hard-coded workload; §3 cmdlet-surface probe |
| 5 | Enabling RSS without populating allow-list | Search drops to zero; users see "no results"; tickets storm in | §6 enables RSS and submits allow-list in one transaction; §10 warns on empty list |
| 6 | Using a stale `Set-SPOTenantRestrictedSearchMode` script after the modern parameter shipped | Sets the wrong setting silently; tenant is not actually restricted | §6 probes for modern parameter and prefers it |
| 7 | Endpoint DLP rule with no Edge in `AllowedBrowsers` | `pasteToCopilot` restriction does not reach Copilot for Web; web prompts leak | §7 hard-fails if Edge missing |
| 8 | Endpoint DLP rule applied to non-onboarded devices | Rule does nothing on devices not enrolled in Defender for Endpoint | §7 guidance + Control 1.10 onboarding gate |
| 9 | Standard SharePoint/OneDrive retention policy assumed to cover Copilot Pages | Pages live in SharePoint Embedded; standard policy does not bind | §8 dedicated retention policy targeting `TeamsChatLocation` and Copilot containers |
| 10 | No preservation lock on Copilot retention policy | Admin can shorten retention later; SEC 17a-4(f) immutability fails | §8 guidance + Control 1.7 (Comprehensive Audit Logging and Compliance) |
| 11 | Treating Copilot Notebook deletion as recoverable from a recycle bin | No user-facing recycle bin; recovery requires admin within retention window | §8 guidance |
| 12 | Skipping `-WhatIf` on first run in production | Drift surface created without rehearsal; rollback hard | §4/§5/§6/§7/§8 mutation pattern requires `-WhatIf` then `-Force` |
| 13 | Ignoring `Disconnected` cached tokens between runs | Stale delegated context masks a missing app role | §2 explicit `Disconnect-MgGraph` at session open |
| 14 | Anthropic enabled in EU/EFTA/UK without admin override review | Customer data may leave EU Data Boundary unexpectedly | §9 multi-geo posture probe; document under Control 2.10 |
| 15 | Running `Set-LabelPolicy` without re-reading the policy after | Cmdlet returns success even when no rule body changed; drift goes unnoticed | §4 after-snapshot and field-level verify |
| 16 | Allowing `BlockAccessScope = 'All'` on grounding-side rule | Generates noisy alerts against anonymous web crawlers; obscures real Copilot violations | §5 enforces `'PerUser'` |
| 17 | Skipping pre-flight gates because "the policy already exists" | Misses license drift, RBAC loss, cmdlet-surface regression | §3 mandatory; `Invoke-Agt47Verification` always runs `Test-Agt47Prerequisites` first |

---

## Cross-references

- **Control 4.7** — [M365 Copilot Data Governance control specification](../../../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md)
- **Control 4.6** — Information Protection labels (label taxonomy is a prerequisite to §4)
- **Control 4.4** — Site Lifecycle (gate to RSS allow-list inclusion in §6)
- **Control 4.5** — DAG Reviews (permission hygiene on RSS-listed sites)
- **Control 3.1** — Activity Audit Log (Copilot interaction audit pipeline)
- **Control 3.5** — Immutable Storage / Preservation Lock (binds the §8 retention policy)
- **Control 3.6** — Risky Use Detection (consumes alerts from §5 and §7)
- **Control 3.13** — Legal Hold (overrides §8 for legal hold scope)
- **Control 2.1** — License Assignment (scope alignment for §4)
- **Control 2.7** — Change Management (governs module pinning updates in §1)
- **Control 2.10** — Procurement Diligence (Anthropic / subprocessor disclosure)
- **Control 1.10** — Defender for Endpoint onboarding (gates §7)
- **PowerShell Baseline** — [Shared module pinning, mutation safety, evidence](../../_shared/powershell-baseline.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
