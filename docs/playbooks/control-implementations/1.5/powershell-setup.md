# Control 1.5 — PowerShell Setup: DLP and Sensitivity Labels

> **Scope.** This playbook automates **inventory, drift detection, and bounded mutation** for Microsoft Purview DLP, sensitivity labels, sensitive-information types (SITs), exact-data-match (EDM) classifiers, keyword dictionaries, Power Platform DLP, and the cross-surface settings that make Control 1.5 enforceable for Microsoft 365 Copilot and agentic workloads in US financial services tenants.
>
> **What this is.** A baseline-conformant authoring guide. Every helper returns `[pscustomobject]` with a `Status` field of `Clean | Anomaly | Pending | NotApplicable | Error`, mutating cmdlets honour `-WhatIf`, and all evidence is hashed via `Write-FsiEvidence`.
>
> **What this isn't.** A substitute for the [portal walkthrough](portal-walkthrough.md), the [verification & testing](verification-testing.md) playbook, or [troubleshooting](troubleshooting.md). It also does not replace tenant-specific risk acceptance for preview features.
>
> **Hedged-language reminder.** PowerShell coverage of Purview DLP **supports compliance with** FINRA 3110 / SEC 17a-4 / GLBA / SOX recordkeeping and supervision obligations. It does not, by itself, *guarantee* compliance — implementation requires policy targeting, label deployment, end-user training, and exception governance.

---

## Metadata

| Field | Value |
|---|---|
| Control ID | 1.5 |
| Pillar | 1 — Security |
| Playbook | PowerShell setup (companion to portal walkthrough, verification, troubleshooting) |
| PowerShell editions | PS 7.4+ for Graph + Exchange; **PS 5.1 Desktop required** for `Microsoft.PowerApps.Administration.PowerShell` mutation cmdlets |
| Cloud | Commercial (Global) |
| Companion playbooks | [portal-walkthrough](portal-walkthrough.md) · [verification-testing](verification-testing.md) · [troubleshooting](troubleshooting.md) |
| Related controls | [1.6 DSPM for AI](../1.6/portal-walkthrough.md) · [1.10 Communication Compliance](../1.10/portal-walkthrough.md) · [1.12 IRM](../1.12/portal-walkthrough.md) · [1.13 SITs/EDM](../1.13/portal-walkthrough.md) · [1.15 DKE/encryption](../1.15/portal-walkthrough.md) · [2.12 Supervision](../2.12/portal-walkthrough.md) · [3.4 Incident reporting](../3.4/portal-walkthrough.md) · [3.9 Sentinel forwarding](../3.9/portal-walkthrough.md) |
| Baseline | [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) |

---

## §0 — READ FIRST: Wrong-shell trap & DLP false-clean defects

Three failure modes silently produce **false-clean evidence** for Control 1.5. Reviewers who do not read this section will sign off on policies that were never actually inspected.

| # | Trap | False-clean symptom | Remediation |
|---|---|---|---|
| 1 | **Wrong DLP plane.** `Get-DlpCompliancePolicy` (Purview) and `Get-DlpPolicy` (Power Platform) are **different cmdlets in different connections**. Running only the first returns "0 anomalies" while every connector policy is missing. | M365 DLP looks complete; connector classification gap is invisible. | Always run **both** planes. The §13 wrapper enforces this; ad-hoc scripts must too. |
| 2 | **Power Platform UI/API label inversion.** API value `Confidential` renders in the Maker portal as **Business**; API `General` renders as **Non-Business**; `Blocked` is `Blocked`. A reviewer comparing a script that prints `General` against a screenshot showing `Non-Business` will (correctly) think they match — and miss that the *intent* was Business. | Connector evidence reads as "expected" but the API label is opposite of the documented business decision. | Always emit **both** labels via `ConvertTo-FsiUiLabel` (§9). |
| 3 | **Audit RecordType = DLP is invalid.** `Search-UnifiedAuditLog -RecordType DLP` returns zero rows on every tenant. Real record types are `ComplianceDLPSharePoint`, `ComplianceDLPSharePointClassification`, `ComplianceDLPExchange`, `ComplianceDLPExchangeClassification`, `DLPEndpoint`. For Copilot, query `-Operations 'DLPRuleMatch'` and filter the payload `Workload -eq 'Applications'`. | "No DLP events in 30 days" — looks like a clean tenant; actually a broken query. | Use the helper `Get-FsiDlpAuditEvents` in §11. |

A fourth trap — **shell mismatch** — is enforced as a guard:

```powershell
# Shell guard — paste at the top of every Control 1.5 script
if ($PSVersionTable.PSEdition -ne 'Core' -and $PSVersionTable.PSVersion.Major -lt 7) {
    # Allowed: PS 5.1 Desktop is required for Power Apps Admin mutation cmdlets (see §9)
    Write-Warning 'Running on PS 5.1 Desktop. Graph + Exchange helpers will work; Power Apps Admin mutations are supported here. For Graph performance, prefer PS 7.4+ in a separate session.'
}
```

---

## §1 — Module / CLI / permission matrix

Pin every module via `Install-Module -RequiredVersion` per the [baseline](../../_shared/powershell-baseline.md). Do not use `-Force` to silently upgrade in production.

| Module | Min version | Edition | Used for | Connect cmdlet | Least-privilege role |
|---|---|---|---|---|---|
| `ExchangeOnlineManagement` | 3.4.0 | PS 7.4+ | Purview DLP, sensitivity labels, label policies, auto-label rules, EDM, dictionaries | `Connect-IPPSSession` | Purview Compliance Admin (or scoped Information Protection Admin + DLP Compliance Mgmt) |
| `Microsoft.Graph.Authentication` | 2.20.0 | PS 7.4+ | Tokens for downstream Graph calls | `Connect-MgGraph` | n/a (delegated by app role) |
| `Microsoft.Graph.Beta.Security` | 2.20.0 | PS 7.4+ | `Get-MgBetaSecurityInformationProtectionSensitivityLabel` (label tenant inventory) | n/a | `InformationProtectionPolicy.Read.All` |
| `Microsoft.Graph.Beta.Compliance` | 2.20.0 | PS 7.4+ | DSPM-for-AI cross-link (Control 1.6) | n/a | `InformationProtectionPolicy.Read.All` |
| `Microsoft.Online.SharePoint.PowerShell` *or* `PnP.PowerShell` | 16.0.25410 / 2.4.0 | PS 7.4+ | SharePoint/OneDrive label-default + DLP scoping | `Connect-SPOService` / `Connect-PnPOnline` | SharePoint Admin |
| `Microsoft.PowerApps.Administration.PowerShell` | 2.0.190 | **PS 5.1 Desktop only** | `Get-DlpPolicy`, `New-DlpPolicy`, `Add-ConnectorToPolicy`, `Set-ConnectorGroup` | `Add-PowerAppsAccount` | Power Platform Admin |
| `Microsoft.PowerApps.PowerShell` | 1.0.34 | PS 5.1 Desktop | Maker-side enumeration | `Add-PowerAppsAccount` | Power Platform Admin |

**Edition guard.** Any helper that calls a `*-DlpPolicy` (Power Platform) cmdlet must be invoked from PS 5.1 Desktop:

```powershell
function Assert-FsiDesktopPowerShell {
    if ($PSVersionTable.PSEdition -ne 'Desktop') {
        throw 'Power Platform DLP cmdlets require PowerShell 5.1 Desktop. Open Windows PowerShell (not pwsh.exe) and re-run.'
    }
}
```

---

## §2 — Authentication bootstrap (`Initialize-FsiDlpSession`)

Connect to the commercial endpoint using the default parameters:

```powershell
function Initialize-FsiDlpSession {
    [CmdletBinding()]
    param(
        [string]$Cloud = 'Commercial',

        [Parameter(Mandatory)] [string]$TenantId,
        [Parameter(Mandatory)] [string]$UserPrincipalName,

        # Optional service-principal-with-certificate flow for unattended runs
        [string]$AppId,
        [string]$CertificateThumbprint
    )

    $ippsCfg = 'https://ps.compliance.protection.outlook.com/powershell-liveid/'


    # Purview / Exchange (IPPS)
    if ($AppId -and $CertificateThumbprint) {
        Connect-IPPSSession -ConnectionUri $ippsCfg -AppId $AppId -CertificateThumbprint $CertificateThumbprint -Organization "$TenantId" -ShowBanner:$false
    } else {
        Connect-IPPSSession -ConnectionUri $ippsCfg -UserPrincipalName $UserPrincipalName -ShowBanner:$false
    }

    # Graph
    Connect-MgGraph -TenantId $TenantId -Environment 'Global' -Scopes 'InformationProtectionPolicy.Read.All','Policy.Read.All' -NoWelcome

    # Power Platform (only on PS 5.1 Desktop)
    if ($PSVersionTable.PSEdition -eq 'Desktop') {
        Add-PowerAppsAccount | Out-Null
    } else {
        Write-Warning 'Skipping Add-PowerAppsAccount: not on PS 5.1 Desktop. Power Platform DLP helpers will return Status=Pending.'
    }

    [pscustomobject]@{
        Status      = 'Clean'
        Cloud       = $Cloud
        TenantId    = $TenantId
        IppsUri     = $ippsCfg
        GraphEnv    = 'Global'
        PowerAppsEp = 'prod'
        Timestamp   = (Get-Date).ToUniversalTime()
    }
}
```

---

## §3 — Helper library overview

| # | Helper | Purpose | Returns `Status` |
|---|---|---|---|
| 1 | `Get-FsiDlpCoverage` (§4) | Map every Purview DLP policy across the 13 surfaces | `Clean` if all surfaces covered; else `Anomaly` |
| 2 | `Get-FsiCopilotDlpPolicies` (§5) | Validate Copilot DLP rule shape (Custom template, `EnforcementPlanes`, `MicrosoftCopilotEnabledLocation`) | `Clean` / `Anomaly` / `Pending` |
| 3 | `Test-FsiPolicyTipOverrideSettings` (§6) | Verify `NotifyAllowOverride='WithJustification'` and override-justification capture | `Clean` / `Anomaly` |
| 4 | `Get-FsiSensitivityLabelInventory` (§7) | Reconcile labels via Graph beta + IPPS | `Clean` / `Anomaly` |
| 5 | `Get-FsiAdaptiveProtectionStatus` (§10) | Detect Adaptive Protection rollout state | `Clean` / `NotApplicable` / `Pending` |

Auxiliary (non-status-bearing) utilities introduced inline: `ConvertTo-FsiUiLabel` (§9), `Get-FsiDlpAuditEvents` (§11), `Invoke-FsiControl15Audit` (§13).

---

## §4 — DLP cmdlet inventory + `Get-FsiDlpCoverage`

The 13 enforcement surfaces tracked by Control 1.5 (the on-prem AIP scanner is recognised in the control doc but is portal-only and out of PS scope):

1. SharePoint sites · 2. OneDrive accounts · 3. Exchange email · 4. Teams chat & channel · 5. Devices (Endpoint DLP) · 6. Copilot — block by sensitivity label (GA) · 7. Copilot — block by SIT (preview) · 8. Power Platform connector classification · 9. Power Platform HTTP endpoint filtering (preview) · 10. Edge for Business unmanaged AI (preview) · 11. Network DLP for unmanaged AI (preview, portal-only) · 12. Defender for Cloud Apps · 13. Power BI / Fabric workspaces.

**Cmdlet inventory (Purview plane).** `Get-DlpCompliancePolicy`, `Get-DlpComplianceRule`, `New-DlpCompliancePolicy`, `Set-DlpCompliancePolicy`, `New-DlpComplianceRule`, `Set-DlpComplianceRule`, `Remove-DlpCompliancePolicy`. Note: DLP policies use the **`Mode`** parameter (`Enable | TestWithNotifications | TestWithoutNotifications | Disable | PendingDeletion`) — there is no `Enabled` Boolean.

```powershell
function Get-FsiDlpCoverage {
    [CmdletBinding()]
    param()

    $surfaces = @(
        'SharePoint','OneDriveForBusiness','ExchangeLocation','TeamsLocation',
        'EndpointDevices','MicrosoftCopilotEnabledLocation','PowerPlatform',
        'EdgeBrowser','NetworkUnmanagedAi','DefenderForCloudApps','PowerBIWorkspaces','OnPremScanner'
    )

    $policies = Get-DlpCompliancePolicy -ErrorAction Stop
    $covered  = @{}
    foreach ($s in $surfaces) { $covered[$s] = $false }

    foreach ($p in $policies) {
        if ($p.Mode -eq 'Disable' -or $p.Mode -eq 'PendingDeletion') { continue }
        if ($p.SharePointLocation)      { $covered.SharePoint = $true }
        if ($p.OneDriveLocation)        { $covered.OneDriveForBusiness = $true }
        if ($p.ExchangeLocation)        { $covered.ExchangeLocation = $true }
        if ($p.TeamsLocation)           { $covered.TeamsLocation = $true }
        if ($p.EndpointDlpLocation)     { $covered.EndpointDevices = $true }
        if ($p.MicrosoftCopilotEnabledLocation) { $covered.MicrosoftCopilotEnabledLocation = $true }
        if ($p.PowerBIDlpLocation)      { $covered.PowerBIWorkspaces = $true }
    }

    $gaps = $covered.GetEnumerator() | Where-Object { -not $_.Value } | Select-Object -ExpandProperty Key

    [pscustomobject]@{
        Status        = if ($gaps.Count -eq 0) { 'Clean' } else { 'Anomaly' }
        PolicyCount   = $policies.Count
        SurfacesCovered = ($covered.GetEnumerator() | Where-Object { $_.Value } | Select-Object -ExpandProperty Key)
        SurfacesMissing = $gaps
        Note          = 'NetworkUnmanagedAi and OnPremScanner are not addressable via PowerShell; verify via portal evidence.'
        Timestamp     = (Get-Date).ToUniversalTime()
    }
}
```

---

## §5 — Copilot DLP policy creation & `Get-FsiCopilotDlpPolicies`

Copilot DLP requires the Purview UI **Custom** template. Two facts trip up most teams:

1. **You cannot combine SIT and sensitivity-label conditions in the same rule.** Use two rules in the same policy.
2. The location object is a JSON blob shaped `[{ "Workload":"Applications" }]` and the policy parameter is `MicrosoftCopilotEnabledLocation`. The rule must declare `EnforcementPlanes=@('CopilotExperiences')`.

```powershell
$copilotLocations = ConvertTo-Json -Compress -InputObject @(@{ Workload = 'Applications' })

New-DlpCompliancePolicy `
    -Name 'FSI-Copilot-MNPI-Block' `
    -MicrosoftCopilotEnabledLocation $copilotLocations `
    -Mode 'TestWithNotifications' `
    -WhatIf

# Rule A — block by sensitivity label (GA)
New-DlpComplianceRule `
    -Name 'BlockHighlyConfidentialFromCopilot' `
    -Policy 'FSI-Copilot-MNPI-Block' `
    -EnforcementPlanes @('CopilotExperiences') `
    -ContentContainsSensitivityLabel @(@{ labels = @('<labelGuidHighlyConfidential>') }) `
    -BlockAccess $true `
    -NotifyUser @('SiteAdmin','LastModifier') `
    -NotifyAllowOverride 'WithJustification' `
    -NotifyEmailCustomText 'This content is restricted from Copilot grounding under FINRA 3110 / SEC 17a-4 controls.' `
    -WhatIf

# Rule B — block by SIT (preview). Separate rule, same policy.
New-DlpComplianceRule `
    -Name 'BlockMnpiSitFromCopilot' `
    -Policy 'FSI-Copilot-MNPI-Block' `
    -EnforcementPlanes @('CopilotExperiences') `
    -ContentContainsSensitiveInformation @(@{ name = '<sitGuidMnpi>'; mincount = 1 }) `
    -BlockAccess $true `
    -WhatIf
```

```powershell
function Get-FsiCopilotDlpPolicies {
    [CmdletBinding()]
    param()

    $policies = Get-DlpCompliancePolicy | Where-Object { $_.MicrosoftCopilotEnabledLocation }
    $findings = foreach ($p in $policies) {
        $rules = Get-DlpComplianceRule -Policy $p.Name
        $copilotRules = $rules | Where-Object { $_.EnforcementPlanes -contains 'CopilotExperiences' }
        $hasLabelRule = $copilotRules | Where-Object { $_.ContentContainsSensitivityLabel }
        $hasSitRule   = $copilotRules | Where-Object { $_.ContentContainsSensitiveInformation }
        $combined     = $copilotRules | Where-Object { $_.ContentContainsSensitivityLabel -and $_.ContentContainsSensitiveInformation }

        $status = if ($combined) { 'Anomaly' }
                  elseif (-not ($hasLabelRule -or $hasSitRule)) { 'Anomaly' }
                  elseif ($p.Mode -ne 'Enable') { 'Pending' }
                  else { 'Clean' }

        [pscustomobject]@{
            Status        = $status
            Policy        = $p.Name
            Mode          = $p.Mode
            LabelRule     = [bool]$hasLabelRule
            SitRule       = [bool]$hasSitRule
            CombinedRule  = [bool]$combined
            RuleCount     = $copilotRules.Count
            Note          = if ($combined) { 'Combined SIT+Label rule detected — split into two rules.' } else { '' }
        }
    }
    if (-not $findings) {
        return [pscustomobject]@{ Status = 'Anomaly'; Policy = '<none>'; Note = 'No Copilot-scoped DLP policies found.' }
    }
    $findings
}
```

---

## §6 — Rules: notifications, overrides, policy tips

`Test-FsiPolicyTipOverrideSettings` validates that overrides require justification (a supervision-evidence requirement that supports compliance with FINRA Rule 3110).

```powershell
function Test-FsiPolicyTipOverrideSettings {
    [CmdletBinding()]
    param([string[]]$PolicyNames)

    $rules = if ($PolicyNames) { $PolicyNames | ForEach-Object { Get-DlpComplianceRule -Policy $_ } }
             else              { Get-DlpComplianceRule }

    $rules | ForEach-Object {
        $needsJustification = ($_.NotifyAllowOverride -contains 'WithJustification')
        $hasNotifyText = -not [string]::IsNullOrWhiteSpace($_.NotifyEmailCustomText)
        $status = if ($needsJustification -and $hasNotifyText) { 'Clean' } else { 'Anomaly' }
        [pscustomobject]@{
            Status                 = $status
            Rule                   = $_.Name
            Policy                 = $_.ParentPolicyName
            NotifyAllowOverride    = ($_.NotifyAllowOverride -join ',')
            NotifyUserType         = ($_.NotifyUser -join ',')
            HasCustomEmailText     = $hasNotifyText
        }
    }
}
```

---

## §7 — Sensitivity labels & label policies

**Cmdlet correction.** The real Graph beta cmdlet is `Get-MgBetaSecurityInformationProtectionSensitivityLabel`. The frequently-cited `Get-MgBetaInformationProtectionSensitivityPolicyLabel` does **not** exist.

Inventory: `Get-Label`, `Get-LabelPolicy`, `Get-AutoSensitivityLabelPolicy`, `Get-AutoSensitivityLabelRule`. Mutation: `New-Label`, `Set-Label`, `New-LabelPolicy`, `Set-LabelPolicy`, `New-AutoSensitivityLabelPolicy`, `New-AutoSensitivityLabelRule`.

```powershell
function Get-FsiSensitivityLabelInventory {
    [CmdletBinding()]
    param()

    $ippsLabels  = Get-Label | Select-Object Guid, DisplayName, ParentId, Priority, ContentType, Disabled
    $ippsPolicies = Get-LabelPolicy | Select-Object Guid, Name, Labels, ScopedLabels, Mode
    try {
        $graphLabels = Get-MgBetaSecurityInformationProtectionSensitivityLabel -All -ErrorAction Stop |
                       Select-Object Id, Name, Description
    } catch {
        $graphLabels = $null
    }

    $ippsIds  = ($ippsLabels  | Select-Object -ExpandProperty Guid) -as [string[]]
    $graphIds = if ($graphLabels) { ($graphLabels | Select-Object -ExpandProperty Id) -as [string[]] } else { @() }
    $delta    = if ($graphLabels) { Compare-Object $ippsIds $graphIds } else { $null }

    [pscustomobject]@{
        Status             = if (-not $graphLabels) { 'Pending' } elseif ($delta) { 'Anomaly' } else { 'Clean' }
        IppsLabelCount     = $ippsLabels.Count
        GraphLabelCount    = if ($graphLabels) { $graphLabels.Count } else { 0 }
        PolicyCount        = $ippsPolicies.Count
        DeltaItems         = $delta
        Note               = if (-not $graphLabels) { 'Graph beta call failed; verify InformationProtectionPolicy.Read.All consent.' } else { '' }
    }
}
```

---

## §8 — SIT / EDM / dictionary authoring (cross-link to Control 1.13)

Read-side: `Get-DataClassification`, `Get-DlpSensitiveInformationType`, `Get-DlpEdmSchema`, `Get-DlpKeywordDictionary`. Mutation: `New-DlpSensitiveInformationType`, `Set-DlpSensitiveInformationType`, `New-DlpEdmSchema`, `Edit-DlpEdmSchema`, `New-DlpKeywordDictionary`, `Set-DlpKeywordDictionary`.

EDM is the canonical mechanism for **MNPI watchlists** (deal-codename rotations, restricted-list tickers). The schema and the upload pipeline live in [Control 1.13](../1.13/portal-walkthrough.md); from Control 1.5 the consumption pattern is:

```powershell
# Surface MNPI EDM and dictionary classifiers for use in DLP rules
$edm   = Get-DlpEdmSchema
$dicts = Get-DlpKeywordDictionary

$edm | Select-Object Name, IsValid, RowCount, LastUpdatedTime
$dicts | Select-Object Name, Identity, FileData.Length

# In a rule definition
# -ContentContainsSensitiveInformation @(@{ name = '<edmSitGuidMnpiTickers>'; mincount = 1 })
```

Authoring an EDM-backed SIT and a dictionary (non-mutating preview):

```powershell
New-DlpEdmSchema -FileData ([Byte[]](Get-Content -Path .\mnpi-schema.xml -Encoding Byte -Raw)) -WhatIf
New-DlpKeywordDictionary -Name 'FSI-MNPI-Codenames' -Description 'Quarterly rotation' `
    -FileData ([Byte[]](Get-Content -Path .\mnpi-codenames.csv -Encoding Byte -Raw)) -WhatIf
```

---

## §9 — Power Platform DLP + UI/API label inversion

**Edition reminder.** Run from PS 5.1 Desktop (`Assert-FsiDesktopPowerShell` from §1). Cmdlets: `Get-DlpPolicy`, `New-DlpPolicy`, `Set-DlpPolicy`, `Remove-DlpPolicy`, `Add-PowerAppsPolicyToTenant`, `Add-ConnectorToPolicy`, `Set-ConnectorGroup`, `Remove-ConnectorFromPolicy`.

```powershell
function ConvertTo-FsiUiLabel {
    [CmdletBinding()]
    param([Parameter(Mandatory)][ValidateSet('Confidential','General','Blocked')] [string]$ApiLabel)
    switch ($ApiLabel) {
        'Confidential' { 'Business' }
        'General'      { 'Non-Business' }
        'Blocked'      { 'Blocked' }
    }
}

function Get-FsiPowerPlatformDlpInventory {
    [CmdletBinding()]
    param()
    Assert-FsiDesktopPowerShell

    $policies = Get-DlpPolicy
    $rows = foreach ($p in $policies.value) {
        foreach ($g in $p.connectorGroups) {
            foreach ($c in $g.connectors) {
                [pscustomobject]@{
                    Status         = 'Clean'
                    Policy         = $p.displayName
                    Environment    = ($p.environments | Select-Object -ExpandProperty name) -join ','
                    Connector      = $c.name
                    ConnectorId    = $c.id
                    ApiLabel       = $g.classification
                    UiLabel        = ConvertTo-FsiUiLabel -ApiLabel $g.classification
                }
            }
        }
    }
    $rows
}
```

> **Evidence requirement.** Always emit **both** `ApiLabel` and `UiLabel`. A reviewer comparing a script that prints `General` against a Maker-portal screenshot showing `Non-Business` will conclude they match — and miss that the documented business decision was `Business` (`Confidential`).

---

## §10 — Adaptive Protection (`Get-FsiAdaptiveProtectionStatus`)

Adaptive Protection / Insider Risk-driven DLP status check:

```powershell
function Get-FsiAdaptiveProtectionStatus {
    [CmdletBinding()]
    param(
        [string] $Cloud = 'Commercial'
    )

    try {
        $ap = Get-DlpAdaptiveProtectionConfiguration -ErrorAction Stop
        [pscustomobject]@{
            Status   = if ($ap.Enabled) { 'Clean' } else { 'Pending' }
            Cloud    = $Cloud
            Enabled  = $ap.Enabled
            Profiles = ($ap.RiskLevels -join ',')
        }
    } catch {
        [pscustomobject]@{ Status = 'Pending'; Cloud = $Cloud; Note = "Cmdlet unavailable: $($_.Exception.Message)" }
    }
}
```

---

## §11 — Audit log queries + Sentinel forwarding

**The trap is real.** `-RecordType DLP` is invalid and returns zero rows on every tenant. Use the explicit record types below; for Copilot, query `-Operations 'DLPRuleMatch'` and filter the payload `Workload -eq 'Applications'`.

```powershell
function Get-FsiDlpAuditEvents {
    [CmdletBinding()]
    param(
        [datetime]$StartDate = (Get-Date).AddDays(-7),
        [datetime]$EndDate   = (Get-Date)
    )

    $recordTypes = @(
        'ComplianceDLPSharePoint',
        'ComplianceDLPSharePointClassification',
        'ComplianceDLPExchange',
        'ComplianceDLPExchangeClassification',
        'DLPEndpoint'
    )

    $rows = foreach ($rt in $recordTypes) {
        Search-UnifiedAuditLog -StartDate $StartDate -EndDate $EndDate -RecordType $rt -ResultSize 5000 |
            Select-Object CreationDate, UserIds, Operations, RecordType, AuditData
    }

    $copilot = Search-UnifiedAuditLog -StartDate $StartDate -EndDate $EndDate -Operations 'DLPRuleMatch' -ResultSize 5000 |
        Where-Object { ($_.AuditData | ConvertFrom-Json).Workload -eq 'Applications' }

    [pscustomobject]@{
        Status         = if (($rows.Count + $copilot.Count) -gt 0) { 'Clean' } else { 'Pending' }
        ClassicEvents  = $rows.Count
        CopilotEvents  = $copilot.Count
        WindowStartUtc = $StartDate.ToUniversalTime()
        WindowEndUtc   = $EndDate.ToUniversalTime()
        Note           = 'Forwarding to Sentinel is owned by Control 3.9.'
    }
}
```

For the Sentinel forwarding pipeline (M365 connector, custom log table, KQL detection rules), see [Control 3.9](../3.9/portal-walkthrough.md).

---

## §12 — 13-surface walkthrough

| # | Surface | PowerShell coverage | Helper / cmdlet | Skip rationale |
|---|---|---|---|---|
| 1 | SharePoint sites | Full | `Get-DlpCompliancePolicy` `.SharePointLocation` |  |
| 2 | OneDrive accounts | Full | `.OneDriveLocation` |  |
| 3 | Exchange email | Full | `.ExchangeLocation` |  |
| 4 | Teams chat / channel | Full | `.TeamsLocation` |  |
| 5 | Endpoint devices | Full | `.EndpointDlpLocation` |  |
| 6 | Copilot — block by label (GA) | Full | `Get-FsiCopilotDlpPolicies` |  |
| 7 | Copilot — block by SIT (preview) | Full | `Get-FsiCopilotDlpPolicies` (Rule B) | Preview; verify portal availability |
| 8 | Power Platform connector classification | Full (PS 5.1) | `Get-FsiPowerPlatformDlpInventory` |  |
| 9 | Power Platform HTTP endpoint filtering (preview) | Full (PS 5.1) | `Get-DlpPolicy` `.endpointConfigurations` | Preview |
| 10 | Edge for Business unmanaged AI (preview) | Partial | `Get-DlpCompliancePolicy` (when surfaced) | Preview; portal evidence required |
| 11 | Network DLP for unmanaged AI (preview) | **None** | n/a | Portal-only; capture screenshot evidence |
| 12 | Defender for Cloud Apps | Indirect | Graph Security API | Owned by MDA team; cross-reference |
| 13 | Power BI / Fabric workspaces | Full | `.PowerBIDlpLocation` |  |

---

## §13 — Wrapper orchestration with transcript & evidence manifest

```powershell
function Invoke-FsiControl15Audit {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [string]$Cloud = 'Commercial',
        [Parameter(Mandatory)] [string]$TenantId,
        [Parameter(Mandatory)] [string]$UserPrincipalName,
        [string]$EvidencePath = (Join-Path $PWD ('control-15-' + (Get-Date -Format 'yyyyMMdd-HHmmss')))
    )

    New-Item -ItemType Directory -Path $EvidencePath -Force | Out-Null
    Start-Transcript -Path (Join-Path $EvidencePath 'transcript.log') -Append | Out-Null

    try {
        $session = Initialize-FsiDlpSession -Cloud $Cloud -TenantId $TenantId -UserPrincipalName $UserPrincipalName

        $results = [ordered]@{
            session             = $session
            dlpCoverage         = Get-FsiDlpCoverage
            copilotPolicies     = Get-FsiCopilotDlpPolicies
            policyTipOverrides  = Test-FsiPolicyTipOverrideSettings
            labelInventory      = Get-FsiSensitivityLabelInventory
            adaptiveProtection  = Get-FsiAdaptiveProtectionStatus -Cloud $Cloud
            dlpAuditEvents      = Get-FsiDlpAuditEvents
        }

        if ($PSVersionTable.PSEdition -eq 'Desktop') {
            $results['powerPlatformDlp'] = Get-FsiPowerPlatformDlpInventory
        } else {
            $results['powerPlatformDlp'] = [pscustomobject]@{ Status = 'Pending'; Note = 'Run from PS 5.1 Desktop.' }
        }

        foreach ($k in $results.Keys) {
            $results[$k] | ConvertTo-Json -Depth 8 | Out-File (Join-Path $EvidencePath "$k.json") -Encoding UTF8
        }

        # Hash + manifest (baseline-conformant)
        Write-FsiEvidence -Path $EvidencePath -ControlId '1.5'

        $rollup = $results.GetEnumerator() | ForEach-Object {
            [pscustomobject]@{ Section = $_.Key; Status = ($_.Value | Select-Object -First 1 -ExpandProperty Status -ErrorAction SilentlyContinue) }
        }
        $rollup
    } finally {
        Stop-Transcript | Out-Null
    }
}
```

---

## §14 — Anti-patterns & cross-references

| Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| Running only `Get-DlpCompliancePolicy` and declaring the tenant clean | Misses every Power Platform connector policy | Run both planes (§4 + §9) |
| `Search-UnifiedAuditLog -RecordType DLP` | Invalid record type — returns zero rows | Use the five record types in §11 |
| Combining SIT + sensitivity label conditions in one Copilot rule | Rule will not save, or will save with silent precedence | Two rules, same policy (§5) |
| Reporting Power Platform DLP labels as `Confidential` / `General` only | Inverted vs the Maker-portal UI; reviewers misread evidence | Emit both via `ConvertTo-FsiUiLabel` (§9) |
| Calling `Get-MgBetaInformationProtectionSensitivityPolicyLabel` | Cmdlet does not exist | Use `Get-MgBetaSecurityInformationProtectionSensitivityLabel` (§7) |
| Using `-Force` on `Install-Module` in production | Silent module upgrade breaks reproducibility | `Install-Module -RequiredVersion` per baseline §1 |
| Treating `Mode = 'Disable'` policies as active | They emit no enforcement | Filter on `Mode -eq 'Enable'` (§4) |
| Running Power Apps Admin cmdlets from `pwsh` 7.x | Cmdlets are Desktop-only; silently no-op or error | `Assert-FsiDesktopPowerShell` (§1) |

**Cross-references.** [1.6 DSPM for AI](../1.6/portal-walkthrough.md) consumes label + SIT signals from this control. [1.10 Communication Compliance](../1.10/portal-walkthrough.md) and [2.12 Supervision](../2.12/portal-walkthrough.md) consume DLP-rule-match signals to drive reviewer queues. [1.12 IRM](../1.12/portal-walkthrough.md) and [1.15 DKE/encryption](../1.15/portal-walkthrough.md) provide the rights-management substrate for label-based blocking. [1.13 SITs/EDM](../1.13/portal-walkthrough.md) owns classifier authoring. [3.4 Incident reporting](../3.4/portal-walkthrough.md) and [3.9 Sentinel forwarding](../3.9/portal-walkthrough.md) own downstream telemetry.

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
